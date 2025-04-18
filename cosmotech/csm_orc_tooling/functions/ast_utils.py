# Copyright (C) - 2023 - 2025 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

"""
AST (Abstract Syntax Tree) utilities for parsing and analyzing Python files.
"""

import ast
import re
from typing import Dict, List, Set, Tuple, Optional


def extract_functions_from_file(file_path: str) -> List[Tuple[str, str]]:
    """
    Extract function names and their fully qualified names from a Python file.

    Args:
        file_path: Path to the Python file

    Returns:
        List of tuples (function_name, fully_qualified_name)
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    module_path = file_path.replace("/", ".").replace("\\", ".").replace(".py", "")
    functions = []

    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Skip private functions (starting with _)
                if node.name.startswith("_") and not node.name.startswith("__"):
                    continue
                functions.append((node.name, f"{module_path}.{node.name}"))
            elif isinstance(node, ast.ClassDef):
                for subnode in node.body:
                    if isinstance(subnode, ast.FunctionDef):
                        # Skip private methods
                        if subnode.name.startswith("_") and not subnode.name.startswith("__"):
                            continue
                        functions.append((f"{node.name}.{subnode.name}", f"{module_path}.{node.name}.{subnode.name}"))
    except SyntaxError:
        print(f"Syntax error in {file_path}")

    return functions


def extract_test_functions_from_file(file_path: str) -> List[str]:
    """
    Extract test function names from a test file.

    Args:
        file_path: Path to the test file

    Returns:
        List of test function names
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    test_functions = []

    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                test_functions.append(node.name)
    except SyntaxError:
        print(f"Syntax error in {file_path}")

    return test_functions


class LoggingCallVisitor(ast.NodeVisitor):
    """AST visitor to find logging calls."""

    def __init__(self):
        self.logging_calls = []
        self.in_except_block = False
        self.current_exception_name = None
        self.except_stack = []  # Stack to handle nested except blocks

    def visit_Try(self, node):
        # Visit the try block normally
        for child in node.body:
            self.visit(child)

        # Visit each except handler
        for handler in node.handlers:
            self.visit(handler)

        # Visit else and finally blocks if they exist
        if node.orelse:
            for child in node.orelse:
                self.visit(child)

        if node.finalbody:
            for child in node.finalbody:
                self.visit(child)

    def visit_ExceptHandler(self, node):
        # Save current state before entering except block
        self.except_stack.append((self.in_except_block, self.current_exception_name))

        # Set except block state
        self.in_except_block = True
        self.current_exception_name = node.name

        # Visit the body of the except block
        for child in node.body:
            self.visit(child)

        # Restore previous state when leaving the except block
        prev_state = self.except_stack.pop()
        self.in_except_block = prev_state[0]
        self.current_exception_name = prev_state[1]

    def visit_Call(self, node):
        # Check for LOGGER.xxx() calls
        if (
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "LOGGER"
            and node.func.attr in ["debug", "info", "warning", "error", "critical", "exception"]
        ):
            # Check if this is logging an exception in an except block
            is_exception_log = False
            if self.in_except_block and self.current_exception_name:
                is_exception_log = self._is_logging_exception(node)

            self.logging_calls.append((node, is_exception_log))

        # Continue visiting other nodes
        self.generic_visit(node)

    def _is_logging_exception(self, node):
        """Check if this logging call is directly logging the exception."""
        if not node.args:
            return False

        # Check each argument for patterns that indicate logging an exception
        for arg in node.args:
            # Direct use of exception variable: LOGGER.error(e)
            if isinstance(arg, ast.Name) and arg.id == self.current_exception_name:
                return True

            # str(e) pattern: LOGGER.error(str(e))
            if (
                isinstance(arg, ast.Call)
                and isinstance(arg.func, ast.Name)
                and arg.func.id == "str"
                and arg.args
                and isinstance(arg.args[0], ast.Name)
                and arg.args[0].id == self.current_exception_name
            ):
                return True

            # f-string with exception: LOGGER.error(f"Error: {e}")
            if isinstance(arg, ast.JoinedStr):
                for value in arg.values:
                    if (
                        isinstance(value, ast.FormattedValue)
                        and isinstance(value.value, ast.Name)
                        and value.value.id == self.current_exception_name
                    ):
                        return True

            # Exception as string concatenation: LOGGER.error("Error: " + str(e))
            if isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Add):
                if self._contains_exception_ref(arg.left) or self._contains_exception_ref(arg.right):
                    return True

        return False

    def _contains_exception_ref(self, node):
        """Check if a node contains a reference to the current exception."""
        if isinstance(node, ast.Name) and node.id == self.current_exception_name:
            return True

        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "str"
            and node.args
            and isinstance(node.args[0], ast.Name)
            and node.args[0].id == self.current_exception_name
        ):
            return True

        return False


def extract_translation_key(node: ast.Call) -> Optional[str]:
    """
    Extract translation key from a T() function call.

    Args:
        node: AST node representing a T() function call

    Returns:
        Translation key string or None if not found
    """
    if not node.args:
        return None

    # Get the first argument which should be the translation key
    key_node = node.args[0]

    # Handle string literals
    if isinstance(key_node, ast.Str):
        return key_node.s

    return None


def find_logging_calls_in_file(file_path: str) -> List[Tuple[int, str, Optional[str], bool]]:
    """
    Find all logging calls in a Python file.

    Args:
        file_path: Path to the Python file

    Returns:
        List of tuples (line_number, log_level, translation_key, is_exception_log)
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    try:
        tree = ast.parse(content)
        visitor = LoggingCallVisitor()
        visitor.visit(tree)

        results = []
        for call_node, is_exception_log in visitor.logging_calls:
            line_number = call_node.lineno
            log_level = call_node.func.attr

            # Check if the first argument is a T() call or T().format() call
            translation_key = None
            if call_node.args:
                first_arg = call_node.args[0]

                # Direct T() call
                if (
                    isinstance(first_arg, ast.Call)
                    and isinstance(first_arg.func, ast.Name)
                    and first_arg.func.id == "T"
                ):
                    translation_key = extract_translation_key(first_arg)

                # T().format() call
                elif (
                    isinstance(first_arg, ast.Call)
                    and isinstance(first_arg.func, ast.Attribute)
                    and first_arg.func.attr == "format"
                    and isinstance(first_arg.func.value, ast.Call)
                    and isinstance(first_arg.func.value.func, ast.Name)
                    and first_arg.func.value.func.id == "T"
                ):
                    translation_key = extract_translation_key(first_arg.func.value)

            results.append((line_number, log_level, translation_key, is_exception_log))

        # If AST parsing didn't find all calls, use regex as fallback
        if not results:
            # Regex patterns for both LOGGER.xxx(T("key")) and LOGGER.xxx(T("key").format(...))
            patterns = [
                r'LOGGER\.(debug|info|warning|error|critical|exception)\s*\(\s*T\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)',
                r'LOGGER\.(debug|info|warning|error|critical|exception)\s*\(\s*T\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)\s*\.format',
            ]

            for pattern in patterns:
                for match in re.finditer(pattern, content):
                    log_level = match.group(1)
                    translation_key = match.group(2)
                    # Get line number by counting newlines
                    line_number = content[: match.start()].count("\n") + 1
                    # Set is_exception_log to False since we can't detect it with regex
                    is_exception_log = False
                    results.append((line_number, log_level, translation_key, is_exception_log))

        return results

    except SyntaxError:
        print(f"Syntax error in file: {file_path}")
        return []

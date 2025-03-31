#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Validation tool for checking logging and translation function calls.

This script:
1. Parses Python files to find all logging calls (LOGGER.debug, LOGGER.info, etc.)
2. Checks if these calls use the translation function T()
3. Verifies if the translation keys exist in the translation files
4. Generates a report of issues found
"""

import os
import re
import ast
import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any


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
    """Extract translation key from a T() function call."""
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

    Returns a list of tuples: (line_number, log_level, translation_key, is_exception_log)
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


def load_translation_files(base_dir: str) -> Dict[str, Dict]:
    """Load all translation YAML files."""
    translation_files = {}

    # Find all translation directories
    translation_dir = Path(base_dir) / "cosmotech" / "translation"
    if not translation_dir.exists():
        return translation_files

    # Recursively find all .yml files
    for yml_file in translation_dir.glob("**/*.yml"):
        # Get relative path components
        rel_path = yml_file.relative_to(translation_dir)
        components = list(rel_path.parts)

        if len(components) >= 2 and "rich" not in components:
            # Format: {namespace}/{locale}/{filename}.yml
            namespace = components[0]
            locale = components[1]

            try:
                with open(yml_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)

                key = f"{namespace}/{locale}"
                translation_files[key] = data
            except Exception as e:
                print(f"Error loading {yml_file}: {e}")
    #         print(data)
    # exit(0)
    return translation_files


def check_translation_key_exists(key: str, translation_files: Dict[str, Dict]) -> Dict[str, bool]:
    """
    Check if a translation key exists in all translation files.

    Returns a dictionary mapping file keys to boolean (exists or not).
    """
    results = {}

    # Parse the key to get namespace and actual key path
    if "." in key:
        namespace, *key_path = key.split(".")
    else:
        # If no namespace specified, can't check
        return results
    # Check each translation file for the namespace
    for file_key, data in translation_files.items():
        file_namespace = file_key.split("/")[0]

        # Skip files from different namespaces
        if file_namespace != namespace:
            continue

        # Navigate through the nested dictionary
        current = data
        key_exists = True

        # Navigate through the rest of the path
        for part in key_path:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                key_exists = False
                break
        results[file_key] = key_exists

    return results


def print_yaml_structure(data, prefix=""):
    """Debug function to print the structure of a YAML file."""
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                print(f"{prefix}{key}:")
                print_yaml_structure(value, prefix + "  ")
            else:
                print(f"{prefix}{key}: {value}")
    elif isinstance(data, list):
        for i, item in enumerate(data):
            print(f"{prefix}[{i}]:")
            print_yaml_structure(item, prefix + "  ")
    else:
        print(f"{prefix}{data}")


def find_python_files(base_dir: str) -> List[str]:
    """Find all Python files in the given directory."""
    python_files = []

    # Only search in the cosmotech folder
    cosmotech_dir = os.path.join(base_dir, "cosmotech")
    if not os.path.exists(cosmotech_dir):
        print(f"Warning: 'cosmotech' directory not found in {base_dir}")
        return python_files

    for root, _, files in os.walk(cosmotech_dir):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))

    return python_files


def main():
    parser = argparse.ArgumentParser(description="Validate logging and translation calls")
    parser.add_argument("--dir", default=".", help="Base directory to scan (default: current directory)")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    args = parser.parse_args()

    base_dir = args.dir
    debug = args.debug

    # Load all translation files
    print("Loading translation files...")
    translation_files = load_translation_files(base_dir)
    print(f"Loaded {len(translation_files)} translation files")

    if debug:
        print("\nTranslation file structure:")
        for file_key, data in translation_files.items():
            print(f"\n{file_key}:")
            print_yaml_structure(data)

    # Find all Python files
    print("Finding Python files...")
    python_files = find_python_files(base_dir)
    print(f"Found {len(python_files)} Python files")

    # Track issues
    logs_without_translation = []
    missing_translation_keys = []

    # Process each Python file
    for file_path in python_files:
        rel_path = os.path.relpath(file_path, base_dir)
        print(f"Processing {rel_path}...")

        logging_calls = find_logging_calls_in_file(file_path)

        for line_number, log_level, translation_key, is_exception_log in logging_calls:
            # Skip logs that are directly logging exceptions
            if is_exception_log:
                if debug:
                    print(f"Skipping exception log at {rel_path}:{line_number}")
                continue

            if not translation_key:
                logs_without_translation.append((rel_path, line_number, log_level))
                continue

            # Check if the translation key exists in all files
            key_exists = check_translation_key_exists(translation_key, translation_files)

            if debug and key_exists:
                print(f"\nChecking key: {translation_key}")
                for file_key, exists in key_exists.items():
                    print(f"  {file_key}: {'Found' if exists else 'Not found'}")

            # If key doesn't exist in any file, report it
            if key_exists and not all(key_exists.values()):
                missing_in = [file_key for file_key, exists in key_exists.items() if not exists]
                missing_translation_keys.append((rel_path, line_number, translation_key, missing_in))

    # Print report
    print("\n" + "=" * 80)
    print("VALIDATION REPORT")
    print("=" * 80)

    print("\nLogging calls without translation:")
    if logs_without_translation:
        for file_path, line_number, log_level in logs_without_translation:
            print(f"  {file_path}:{line_number} - LOGGER.{log_level}()")
    else:
        print("  None found")

    print("\nMissing translation keys:")
    if missing_translation_keys:
        for file_path, line_number, key, missing_in in missing_translation_keys:
            print(f"  {file_path}:{line_number} - Key '{key}' missing in: {', '.join(missing_in)}")
    else:
        print("  None found")

    print("\nSummary:")
    print(f"  Total logging calls without translation: {len(logs_without_translation)}")
    print(f"  Total missing translation keys: {len(missing_translation_keys)}")
    print("=" * 80)


if __name__ == "__main__":
    main()

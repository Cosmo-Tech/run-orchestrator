#!/usr/bin/env python3
"""
Script to find functions in the cosmotech.orchestrator module that don't have corresponding tests.
"""

import ast
import importlib
import inspect
import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Colors for terminal output
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

# Directories to scan
SOURCE_DIR = "cosmotech/orchestrator"
TEST_DIR = "tests/unit/orchestrator"


def find_python_files(directory: str) -> List[str]:
    """Find all Python files in a directory recursively."""
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    return python_files


def extract_functions_from_file(file_path: str) -> List[Tuple[str, str]]:
    """Extract function names and their full qualified names from a Python file."""
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
                        functions.append((subnode.name, f"{module_path}.{node.name}.{subnode.name}"))
    except SyntaxError:
        print(f"{RED}Syntax error in {file_path}{RESET}")

    return functions


def extract_test_functions_from_file(file_path: str) -> List[str]:
    """Extract test function names from a test file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    test_functions = []

    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                test_functions.append(node.name)
    except SyntaxError:
        print(f"{RED}Syntax error in {file_path}{RESET}")

    return test_functions


def find_source_functions() -> Dict[str, List[Tuple[str, str]]]:
    """Find all functions in the source code."""
    source_files = find_python_files(SOURCE_DIR)
    source_functions = {}

    for file_path in source_files:
        if "__pycache__" in file_path:
            continue
        functions = extract_functions_from_file(file_path)
        if functions:
            source_functions[file_path] = functions

    return source_functions


def find_test_functions() -> Dict[str, List[str]]:
    """Find all test functions."""
    test_files = find_python_files(TEST_DIR)
    test_functions = {}

    for file_path in test_files:
        if "__pycache__" in file_path:
            continue
        functions = extract_test_functions_from_file(file_path)
        if functions:
            test_functions[file_path] = functions

    return test_functions


def find_untested_functions() -> Dict[str, List[Tuple[str, str]]]:
    """Find functions that don't have corresponding tests."""
    source_functions = find_source_functions()
    test_functions = find_test_functions()

    # Flatten test functions
    all_test_functions = set()
    for functions in test_functions.values():
        all_test_functions.update(functions)

    untested_functions = {}

    for file_path, functions in source_functions.items():
        untested = []
        for func_name, full_name in functions:
            # Check if there's a test for this function
            if not any(test.endswith(f"test_{func_name}") for test in all_test_functions):
                untested.append((func_name, full_name))

        if untested:
            untested_functions[file_path] = untested

    return untested_functions


def main():
    """Main function."""
    untested_functions = find_untested_functions()

    if not untested_functions:
        print(f"{GREEN}All functions have corresponding tests!{RESET}")
        return 0

    print(f"{RED}Found functions without tests:{RESET}")
    total_untested = 0

    for file_path, functions in untested_functions.items():
        print(f"\n{BLUE}{file_path}{RESET}:")
        for func_name, full_name in functions:
            print(f"  - {func_name}")
            total_untested += 1

    print(f"\n{RED}Total untested functions: {total_untested}{RESET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

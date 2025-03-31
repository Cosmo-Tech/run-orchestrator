#!/usr/bin/env python3
"""
Script to generate test files for untested functions in the cosmotech.orchestrator module.
"""

import argparse
import ast
import importlib
import inspect
import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Import the find_untested_functions script from the same directory
import find_untested_functions

# Colors for terminal output
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

# Directories
SOURCE_DIR = "cosmotech/orchestrator"
TEST_DIR = "tests/unit/orchestrator"


def get_function_signature(module_path: str, function_name: str) -> str:
    """Get the signature of a function."""
    try:
        # Try to import the module
        module_parts = module_path.split(".")
        if len(module_parts) > 1 and module_parts[-2] == module_parts[-1]:
            # Handle cases like module.module.function
            module_path = ".".join(module_parts[:-1])

        module = importlib.import_module(module_path)

        # Get the function or method
        if "." in function_name:
            # It's a method
            class_name, method_name = function_name.split(".")
            cls = getattr(module, class_name)
            func = getattr(cls, method_name)
        else:
            # It's a function
            func = getattr(module, function_name)

        # Get the signature
        sig = inspect.signature(func)
        return str(sig)
    except (ImportError, AttributeError) as e:
        print(f"{YELLOW}Warning: Could not get signature for {module_path}.{function_name}: {e}{RESET}")
        return "()"


def generate_test_file_content(module_path: str, functions: List[Tuple[str, str]]) -> str:
    """Generate the content for a test file."""
    module_name = module_path.split(".")[-1]

    # Generate imports
    imports = [
        "import pytest",
        "from unittest.mock import MagicMock, patch",
        f"from {module_path} import *",
        "",
        "",
    ]

    # Generate test functions
    test_functions = []
    for func_name, full_name in functions:
        if "." in func_name:  # It's a method
            class_name, method_name = func_name.split(".")
            signature = get_function_signature(module_path, func_name)
            test_functions.extend(
                [
                    f"def test_{method_name}():",
                    f"    # TODO: Implement test for {class_name}.{method_name}{signature}",
                    "    pass",
                    "",
                    "",
                ]
            )
        else:  # It's a function
            signature = get_function_signature(module_path, func_name)
            test_functions.extend(
                [
                    f"def test_{func_name}():",
                    f"    # TODO: Implement test for {func_name}{signature}",
                    "    pass",
                    "",
                    "",
                ]
            )

    return "\n".join(imports + test_functions)


def generate_test_file(module_path: str, functions: List[Tuple[str, str]]) -> str:
    """Generate a test file for a module."""
    # Convert module path to test file path
    module_parts = module_path.split(".")[2:]
    *module_parts, module_name = module_parts
    test_file_name = f"test_{module_name}.py"

    # Create test directory if it doesn't exist
    test_dir = os.path.join(TEST_DIR, *module_parts)
    os.makedirs(test_dir, exist_ok=True)

    # Generate test file path
    test_file_path = os.path.join(test_dir, test_file_name)

    # Check if the test file already exists
    if os.path.exists(test_file_path):
        print(f"{YELLOW}Warning: Test file {test_file_path} already exists. Skipping.{RESET}")
        return test_file_path

    # Generate test file content
    content = generate_test_file_content(module_path, functions)

    # Write the test file
    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"{GREEN}Generated test file: {test_file_path}{RESET}")
    return test_file_path


def generate_test_files_for_module(module_path: str) -> List[str]:
    """Generate test files for a specific module."""
    # Find all functions in the module
    source_files = find_untested_functions.find_python_files(SOURCE_DIR)
    module_file = None

    for file_path in source_files:
        if module_path in file_path:
            module_file = file_path
            break

    if not module_file:
        print(f"{RED}Error: Module {module_path} not found.{RESET}")
        return []

    functions = find_untested_functions.extract_functions_from_file(module_file)
    if not functions:
        print(f"{YELLOW}No functions found in {module_path}.{RESET}")
        return []

    # Generate test file
    test_file = generate_test_file(module_path.replace("/", ".").replace("\\", ".").replace(".py", ""), functions)
    return [test_file]


def generate_test_files_for_all_untested() -> List[str]:
    """Generate test files for all untested functions."""
    untested_functions = find_untested_functions.find_untested_functions()

    if not untested_functions:
        print(f"{GREEN}All functions have corresponding tests!{RESET}")
        return []

    test_files = []
    for file_path, functions in untested_functions.items():
        module_path = file_path.replace("/", ".").replace("\\", ".").replace(".py", "")
        test_file = generate_test_file(module_path, functions)
        test_files.append(test_file)

    return test_files


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Generate test files for untested functions.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--module", help="Generate test files for a specific module")
    group.add_argument("--all", action="store_true", help="Generate test files for all untested functions")

    args = parser.parse_args()

    if args.module:
        test_files = generate_test_files_for_module(args.module)
    else:
        test_files = generate_test_files_for_all_untested()

    if test_files:
        print(f"\n{GREEN}Generated {len(test_files)} test files.{RESET}")
    else:
        print(f"\n{YELLOW}No test files were generated.{RESET}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

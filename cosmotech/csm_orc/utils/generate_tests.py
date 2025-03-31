# Copyright (C) - 2023 - 2025 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import importlib
import inspect
import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

from cosmotech.orchestrator.utils.click import click
from cosmotech.orchestrator.utils.decorators import web_help
from cosmotech.orchestrator.utils.logger import LOGGER
from cosmotech.orchestrator.utils.translate import T

# Import utility modules
from cosmotech.orchestrator.utils.scripts.colors import RED, GREEN, YELLOW, BLUE, RESET
from cosmotech.orchestrator.utils.scripts.file_utils import find_python_files
from cosmotech.orchestrator.utils.scripts.ast_utils import extract_functions_from_file

# Import the find_untested functionality
from cosmotech.csm_orc.utils.find_untested import find_untested_command


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
        LOGGER.warning(f"{YELLOW}Warning: Could not get signature for {module_path}.{function_name}: {e}{RESET}")
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


def generate_test_file(module_path: str, functions: List[Tuple[str, str]], source_dir: str, test_dir: str) -> str:
    """Generate a test file for a module."""
    # Convert module path to test file path
    module_parts = module_path.split(".")

    # Extract the parts after the source directory
    source_dir_parts = source_dir.split("/")
    module_parts = module_parts[len(source_dir_parts) :]

    *module_parts, module_name = module_parts
    test_file_name = f"test_{module_name}.py"

    # Create test directory if it doesn't exist
    test_dir_path = os.path.join(test_dir, *module_parts)
    os.makedirs(test_dir_path, exist_ok=True)

    # Generate test file path
    test_file_path = os.path.join(test_dir_path, test_file_name)

    # Check if the test file already exists
    if os.path.exists(test_file_path):
        LOGGER.warning(f"{YELLOW}Warning: Test file {test_file_path} already exists. Skipping.{RESET}")
        return test_file_path

    # Generate test file content
    content = generate_test_file_content(module_path, functions)

    # Write the test file
    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write(content)

    LOGGER.info(f"{GREEN}Generated test file: {test_file_path}{RESET}")
    return test_file_path


def find_source_functions(source_dir: str) -> Dict[str, List[Tuple[str, str]]]:
    """Find all functions in the source code."""
    source_files = find_python_files(source_dir)
    source_functions = {}

    for file_path in source_files:
        if "__pycache__" in file_path:
            continue
        functions = extract_functions_from_file(file_path)
        if functions:
            source_functions[file_path] = functions

    return source_functions


def find_test_functions(test_dir: str) -> Dict[str, List[str]]:
    """Find all test functions."""
    test_files = find_python_files(test_dir)
    test_functions = {}

    for file_path in test_files:
        if "__pycache__" in file_path:
            continue
        functions = extract_functions_from_file(file_path)
        if functions:
            test_functions[file_path] = [func_name for func_name, _ in functions]

    return test_functions


def find_untested_functions(source_dir: str, test_dir: str) -> Dict[str, List[Tuple[str, str]]]:
    """Find functions that don't have corresponding tests."""
    source_functions = find_source_functions(source_dir)
    test_functions = find_test_functions(test_dir)

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


def generate_test_files_for_module(module_path: str, source_dir: str, test_dir: str) -> List[str]:
    """Generate test files for a specific module."""
    # Find all functions in the module
    source_files = find_python_files(source_dir)
    module_file = None

    for file_path in source_files:
        if module_path in file_path:
            module_file = file_path
            break

    if not module_file:
        LOGGER.error(f"{RED}Error: Module {module_path} not found.{RESET}")
        return []

    functions = extract_functions_from_file(module_file)
    if not functions:
        LOGGER.warning(f"{YELLOW}No functions found in {module_path}.{RESET}")
        return []

    # Generate test file
    module_path_dotted = module_file.replace("/", ".").replace("\\", ".").replace(".py", "")
    test_file = generate_test_file(module_path_dotted, functions, source_dir, test_dir)
    return [test_file]


def generate_test_files_for_all_untested(source_dir: str, test_dir: str) -> List[str]:
    """Generate test files for all untested functions."""
    untested_functions = find_untested_functions(source_dir, test_dir)

    if not untested_functions:
        LOGGER.info(f"{GREEN}All functions have corresponding tests!{RESET}")
        return []

    test_files = []
    for file_path, functions in untested_functions.items():
        module_path = file_path.replace("/", ".").replace("\\", ".").replace(".py", "")
        test_file = generate_test_file(module_path, functions, source_dir, test_dir)
        test_files.append(test_file)

    return test_files


@click.command()
@click.option("--source-dir", default=SOURCE_DIR, help="Source directory to scan")
@click.option("--test-dir", default=TEST_DIR, help="Test directory to scan")
@click.option("--module", help="Generate test files for a specific module")
@click.option("--all", "generate_all", is_flag=True, help="Generate test files for all untested functions")
@web_help("commands/utils/generate_tests")
def generate_tests_command(source_dir, test_dir, module, generate_all):
    """Generate test files for untested functions"""

    if not (module or generate_all):
        LOGGER.error(T("Please specify either --module or --all"))
        raise click.Abort()

    if module:
        test_files = generate_test_files_for_module(module, source_dir, test_dir)
    else:
        test_files = generate_test_files_for_all_untested(source_dir, test_dir)

    if test_files:
        LOGGER.info(f"\n{GREEN}Generated {len(test_files)} test files.{RESET}")
    else:
        LOGGER.warning(f"\n{YELLOW}No test files were generated.{RESET}")

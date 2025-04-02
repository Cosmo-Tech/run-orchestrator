# Copyright (C) - 2023 - 2025 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from cosmotech.orchestrator.utils.click import click
from cosmotech.orchestrator.utils.logger import LOGGER
from cosmotech.orchestrator.utils.scripts.ast_utils import extract_functions_from_file
from cosmotech.orchestrator.utils.scripts.ast_utils import extract_test_functions_from_file
from cosmotech.orchestrator.utils.scripts.colors import BLUE
from cosmotech.orchestrator.utils.scripts.colors import GREEN
from cosmotech.orchestrator.utils.scripts.colors import RED
from cosmotech.orchestrator.utils.scripts.colors import RESET
from cosmotech.orchestrator.utils.scripts.file_utils import find_python_files


@click.command()
@click.option("--source-dir", default="cosmotech/orchestrator", help="Source directory to scan")
@click.option("--test-dir", default="tests/unit/orchestrator", help="Test directory to scan")
def find_untested_command(source_dir, test_dir):
    """Find functions in the source code that don't have corresponding tests"""

    # Find all functions in the source code
    source_files = find_python_files(source_dir)
    source_functions = {}

    for file_path in source_files:
        if "__pycache__" in file_path:
            continue
        functions = extract_functions_from_file(file_path)
        if functions:
            source_functions[file_path] = functions

    # Find all test functions
    test_files = find_python_files(test_dir)
    test_functions = {}

    for file_path in test_files:
        if "__pycache__" in file_path:
            continue
        functions = extract_test_functions_from_file(file_path)
        if functions:
            test_functions[file_path] = functions

    # Flatten test functions
    all_test_functions = set()
    for functions in test_functions.values():
        all_test_functions.update(functions)

    # Find untested functions
    untested_functions = {}

    for file_path, functions in source_functions.items():
        untested = []
        for func_name, full_name in functions:
            # Check if there's a test for this function
            if not any(test.endswith(f"test_{func_name}") for test in all_test_functions):
                untested.append((func_name, full_name))

        if untested:
            untested_functions[file_path] = untested

    # Print results
    if not untested_functions:
        LOGGER.info(f"{GREEN}All functions have corresponding tests!{RESET}")
        return

    LOGGER.info(f"{RED}Found functions without tests:{RESET}")
    total_untested = 0

    for file_path, functions in untested_functions.items():
        LOGGER.info(f"\n{BLUE}{file_path}{RESET}:")
        for func_name, full_name in functions:
            LOGGER.info(f"  - {func_name}")
            total_untested += 1

    LOGGER.info(f"\n{RED}Total untested functions: {total_untested}{RESET}")

    # Return error code if untested functions were found
    if untested_functions:
        raise click.Abort()

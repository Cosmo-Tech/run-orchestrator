# Copyright (C) - 2023 - 2025 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import os
import argparse
from typing import Dict, List, Set, Tuple, Optional

from cosmotech.orchestrator.utils.click import click
from cosmotech.orchestrator.utils.decorators import web_help
from cosmotech.orchestrator.utils.logger import LOGGER
from cosmotech.orchestrator.utils.translate import T

# Import utility modules
from cosmotech.orchestrator.utils.scripts.yaml_utils import load_translation_files, print_yaml_structure
from cosmotech.orchestrator.utils.scripts.file_utils import find_python_files
from cosmotech.orchestrator.utils.scripts.ast_utils import find_logging_calls_in_file
from cosmotech.orchestrator.utils.scripts.translation_utils import check_translation_key_exists


@click.command()
@click.option("--dir", default=".", help="Base directory to scan (default: current directory)")
@click.option("--debug", is_flag=True, help="Enable debug output")
@web_help("commands/utils/validate_translations")
def validate_translations_command(dir, debug):
    """Validate logging and translation calls"""

    base_dir = dir

    # Load all translation files
    LOGGER.info(T("Loading translation files..."))
    translation_files = load_translation_files(base_dir)
    LOGGER.info(T(f"Loaded {len(translation_files)} translation files"))

    if debug:
        LOGGER.info(T("\nTranslation file structure:"))
        for file_key, data in translation_files.items():
            LOGGER.info(f"\n{file_key}:")
            print_yaml_structure(data)

    # Find all Python files
    LOGGER.info(T("Finding Python files..."))
    python_files = find_python_files(base_dir)
    LOGGER.info(T(f"Found {len(python_files)} Python files"))

    # Track issues
    logs_without_translation = []
    missing_translation_keys = []

    # Process each Python file
    for file_path in python_files:
        rel_path = os.path.relpath(file_path, base_dir)
        LOGGER.info(T(f"Processing {rel_path}..."))

        logging_calls = find_logging_calls_in_file(file_path)

        for line_number, log_level, translation_key, is_exception_log in logging_calls:
            # Skip logs that are directly logging exceptions
            if is_exception_log:
                if debug:
                    LOGGER.debug(T(f"Skipping exception log at {rel_path}:{line_number}"))
                continue

            if not translation_key:
                logs_without_translation.append((rel_path, line_number, log_level))
                continue

            # Check if the translation key exists in all files
            key_exists = check_translation_key_exists(translation_key, translation_files)

            if debug and key_exists:
                LOGGER.debug(T(f"\nChecking key: {translation_key}"))
                for file_key, exists in key_exists.items():
                    LOGGER.debug(T(f"  {file_key}: {'Found' if exists else 'Not found'}"))

            # If key doesn't exist in any file, report it
            if key_exists and not all(key_exists.values()):
                missing_in = [file_key for file_key, exists in key_exists.items() if not exists]
                missing_translation_keys.append((rel_path, line_number, translation_key, missing_in))

    # Print report
    LOGGER.info("\n" + "=" * 80)
    LOGGER.info(T("VALIDATION REPORT"))
    LOGGER.info("=" * 80)

    LOGGER.info(T("\nLogging calls without translation:"))
    if logs_without_translation:
        for file_path, line_number, log_level in logs_without_translation:
            LOGGER.info(T(f"  {file_path}:{line_number} - LOGGER.{log_level}()"))
    else:
        LOGGER.info(T("  None found"))

    LOGGER.info(T("\nMissing translation keys:"))
    if missing_translation_keys:
        for file_path, line_number, key, missing_in in missing_translation_keys:
            LOGGER.info(T(f"  {file_path}:{line_number} - Key '{key}' missing in: {', '.join(missing_in)}"))
    else:
        LOGGER.info(T("  None found"))

    LOGGER.info(T("\nSummary:"))
    LOGGER.info(T(f"  Total logging calls without translation: {len(logs_without_translation)}"))
    LOGGER.info(T(f"  Total missing translation keys: {len(missing_translation_keys)}"))
    LOGGER.info("=" * 80)

    # Return error code if issues were found
    if logs_without_translation or missing_translation_keys:
        raise click.Abort()

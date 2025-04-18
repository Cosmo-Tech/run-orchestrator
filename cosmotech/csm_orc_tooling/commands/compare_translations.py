# Copyright (C) - 2023 - 2025 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import os

from cosmotech.orchestrator.utils.click import click
from cosmotech.orchestrator.utils.logger import LOGGER
from cosmotech.csm_orc_tooling.functions.file_utils import find_translation_files
from cosmotech.csm_orc_tooling.functions.translation_utils import compare_yaml_files

# Import utility modules
from cosmotech.csm_orc_tooling.functions.yaml_utils import load_yaml_file
from cosmotech.orchestrator.utils.translate import T


@click.command()
@click.option("--file1", help="First translation file")
@click.option("--file2", help="Second translation file")
@click.option("--dir", default=".", help="Base directory to scan for translation files")
@click.option("--list", "list_flag", is_flag=True, help="List available translation files")
@click.option("--namespace", help="Compare all files in a specific namespace")
def compare_translations_command(file1, file2, dir, list_flag, namespace):
    """Compare translation files for missing keys"""

    # If list flag is provided, just list available translation files
    if list_flag:
        translation_files = find_translation_files(dir)

        LOGGER.info(T("Available translation files:"))
        for namespace, files in translation_files.items():
            LOGGER.info(f"Namespace: {namespace}")
            for file_path in files:
                LOGGER.info(f"  {file_path}")

        return

    # If namespace is provided, compare all files in that namespace
    if namespace:
        translation_files = find_translation_files(dir)

        if namespace not in translation_files:
            LOGGER.error(T(f"Namespace '{namespace}' not found"))
            raise click.Abort()

        files = list(sorted(translation_files[namespace]))

        if len(files) < 2:
            LOGGER.error(T(f"Not enough files in namespace '{namespace}' to compare"))
            raise click.Abort()

        # Compare each pair of files
        for j in range(1, len(files)):
            file1_path = files[0]
            file2_path = files[j]

            LOGGER.info(T("Comparing:"))
            LOGGER.info(T(f"  File 1: {file1_path}"))
            LOGGER.info(T(f"  File 2: {file2_path}"))

            missing_in_file2, missing_in_file1 = compare_yaml_files(file1_path, file2_path, load_yaml_file)

            LOGGER.info(T("Keys in File 1 but missing in File 2:"))
            if missing_in_file2:
                for key in sorted(missing_in_file2):
                    LOGGER.info(f"  {key}")
            else:
                LOGGER.info(T("  None"))

            LOGGER.info(T("Keys in File 2 but missing in File 1:"))
            if missing_in_file1:
                for key in sorted(missing_in_file1):
                    LOGGER.info(f"  {key}")
            else:
                LOGGER.info(T("  None"))

        return

    # If specific files are provided, compare them
    if file1 and file2:
        file1_path = file1
        file2_path = file2

        if not os.path.exists(file1_path):
            LOGGER.error(T(f"File not found: {file1_path}"))
            raise click.Abort()

        if not os.path.exists(file2_path):
            LOGGER.error(T(f"File not found: {file2_path}"))
            raise click.Abort()

        LOGGER.info(T(f"Comparing:"))
        LOGGER.info(T(f"  File 1: {file1_path}"))
        LOGGER.info(T(f"  File 2: {file2_path}"))

        missing_in_file2, missing_in_file1 = compare_yaml_files(file1_path, file2_path, load_yaml_file)

        LOGGER.info(T("Keys in File 1 but missing in File 2:"))
        if missing_in_file2:
            for key in sorted(missing_in_file2):
                LOGGER.info(f"  {key}")
        else:
            LOGGER.info(T("  None"))

        LOGGER.info(T("Keys in File 2 but missing in File 1:"))
        if missing_in_file1:
            for key in sorted(missing_in_file1):
                LOGGER.info(f"  {key}")
        else:
            LOGGER.info(T("  None"))

        return

    # If we get here, not enough arguments were provided
    LOGGER.error(T("Please provide either --file1 and --file2, --namespace, or --list"))
    raise click.Abort()

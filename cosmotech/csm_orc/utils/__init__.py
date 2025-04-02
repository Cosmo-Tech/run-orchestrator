# Copyright (C) - 2023 - 2025 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from cosmotech.csm_orc.utils.compare_translations import compare_translations_command
from cosmotech.csm_orc.utils.find_untested import find_untested_command
from cosmotech.csm_orc.utils.generate_tests import generate_tests_command
from cosmotech.csm_orc.utils.validate_translations import validate_translations_command
from cosmotech.orchestrator.utils.click import click


@click.group(hidden=True)
def utils_group():
    """Utility commands for development and maintenance"""
    pass


utils_group.add_command(compare_translations_command, "compare-translations")
utils_group.add_command(validate_translations_command, "validate-translations")
utils_group.add_command(find_untested_command, "find-untested")
utils_group.add_command(generate_tests_command, "generate-tests")

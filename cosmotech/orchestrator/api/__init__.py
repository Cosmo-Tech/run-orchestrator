# Copyright (C) - 2023 - 2025 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

"""
API module for the Cosmotech Orchestrator.

This module provides functions that implement the core functionality of the
csm-orc CLI commands, allowing them to be used directly without the CLI context.
"""

from cosmotech.orchestrator.api.run import run_template, validate_template, generate_env_file, display_environment
from cosmotech.orchestrator.api.templates import list_templates, get_template_details, load_template_from_file
from cosmotech.orchestrator.api.entrypoint import run_entrypoint, get_entrypoint_env, run_direct_simulator

__all__ = [
    "run_template",
    "validate_template",
    "generate_env_file",
    "display_environment",
    "list_templates",
    "get_template_details",
    "load_template_from_file",
    "run_entrypoint",
    "get_entrypoint_env",
    "run_direct_simulator",
]

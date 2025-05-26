# Copyright (C) - 2023 - 2025 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

"""
API functions for working with templates.

This module provides functions that implement the core functionality of the
csm-orc list-templates command, allowing them to be used directly without the CLI context.
"""

import os
import pprint
from typing import List, Dict, Any, Optional, Union

from cosmotech.orchestrator.core.command_template import CommandTemplate
from cosmotech.orchestrator.core.orchestrator import FileLoader
from cosmotech.orchestrator.templates.library import Library
from cosmotech.orchestrator.utils.logger import LOGGER
from cosmotech.orchestrator.utils.translate import T


def template_to_dict(template: CommandTemplate, verbose: bool = False, isExitCommand: bool = False) -> Dict[str, Any]:
    """
    Convert a template to a dictionary representation.

    Args:
        template: The template to convert
        verbose: Whether to include all template details

    Returns:
        Dictionary representation of the template
    """
    if verbose:
        # Return all template details
        return {
            "id": template.id,
            "description": template.description,
            "command": template.command,
            "arguments": template.arguments,
            "environment": template.environment,
            "sourcePlugin": template.sourcePlugin,
            "isExitHandler": isExitCommand,
        }
    else:
        # Return basic template info
        return {
            "id": template.id,
            "description": template.description,
            "sourcePlugin": template.sourcePlugin,
        }


def get_template_details(template_id: str, verbose: bool = True) -> Optional[Dict[str, Any]]:
    """
    Get details for a specific template.

    Args:
        template_id: ID of the template to get details for
        verbose: Whether to include all template details

    Returns:
        Dictionary with template details or None if not found
    """
    library = Library()
    template = library.find_template_by_name(template_id)

    if template is None:
        LOGGER.warning(T("csm-orc.cli.templates.template_invalid").format(template_id=template_id))
        return None

    return template_to_dict(template, verbose)


def load_template_from_file(file_path: str) -> bool:
    """
    Load templates from an orchestration file.

    Args:
        file_path: Path to the orchestration file

    Returns:
        True if templates were loaded successfully, False otherwise
    """
    try:
        FileLoader(file_path)()
        return True
    except Exception as e:
        LOGGER.error(f"Error loading templates from file: {e}")
        return False


def list_templates(
    template_ids: List[str] = None, orchestration_file: Optional[str] = None, verbose: bool = False
) -> List[Dict[str, Any]]:
    """
    List available templates.

    Args:
        template_ids: List of template IDs to filter by
        orchestration_file: Path to an orchestration file to add to the library
        verbose: Whether to include full template details

    Returns:
        List of template information dictionaries
    """
    if template_ids is None:
        template_ids = []

    if orchestration_file:
        load_template_from_file(orchestration_file)

    library = Library()

    if not library.templates:
        LOGGER.warning(T("csm-orc.cli.templates.no_templates"))
        return []

    result = []

    if template_ids:
        # Return details for specific templates
        for template_id in template_ids:
            template_info = get_template_details(template_id, verbose)
            if template_info:
                result.append(template_info)
    else:
        # Return all templates
        for template in library.templates:
            result.append(template_to_dict(template, verbose, template.id in library.list_exit_commands()))

    return result


def display_template(template: Union[CommandTemplate, Dict[str, Any]], verbose: bool = False) -> None:
    """
    Display information about a template.

    Args:
        template: The template to display
        verbose: Whether to display all template details
    """
    if isinstance(template, dict):
        # If template is already a dictionary
        template_dict = template
    else:
        # Convert template to dictionary
        template_dict = template_to_dict(template, verbose)

    if verbose:
        LOGGER.info(
            T("csm-orc.cli.templates.template_info").format(
                template=pprint.pformat(template_dict, width=os.get_terminal_size().columns)
            )
        )
    else:
        _desc = f": '{template_dict['description']}'" if template_dict.get("description") else ""
        LOGGER.info(T("csm-orc.cli.templates.template_desc").format(id=template_dict["id"], description=_desc))

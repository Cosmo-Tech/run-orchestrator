# Copyright (C) - 2023 - 2025 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from cosmotech.orchestrator.api.templates import (
    list_templates,
    get_template_details,
    load_template_from_file,
    display_template,
)
from cosmotech.orchestrator.utils.click import click
from cosmotech.orchestrator.utils.decorators import web_help
from cosmotech.orchestrator.utils.logger import LOGGER
from cosmotech.orchestrator.utils.translate import T


@click.command()
@click.option(
    "-t",
    "--template-id",
    "templates",
    multiple=True,
    default=[],
    type=str,
    help="A template id to check for, can be used multiple times",
)
@click.option(
    "-f",
    "--file",
    "orchestration_file",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    help="An orchestration file to add to the library",
)
@click.option(
    "-v", "--verbose", is_flag=True, default=False, help="Display full information on the resulting templates"
)
@web_help("commands/list_templates")
def list_templates_command(templates, orchestration_file, verbose):
    """Show a list of pre-available command templates"""

    # Load templates from file if specified
    if orchestration_file:
        load_template_from_file(orchestration_file)

    # Get and display templates
    if templates:
        # Display specific templates
        for template_id in templates:
            template_info = get_template_details(template_id, verbose=True)
            if template_info:
                display_template(template_info, verbose=True)
    else:
        # Display all templates
        templates_list = list_templates(verbose=verbose)
        if not templates_list:
            return

        for template_dict in templates_list:
            display_template(template_dict, verbose=verbose)

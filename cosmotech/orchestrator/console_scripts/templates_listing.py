# Copyright (C) - 2023 - 2023 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import logging
import os
import pprint

from rich.logging import RichHandler

from cosmotech.orchestrator.templates.library import Library
from cosmotech.orchestrator.utils.click import click
from cosmotech.orchestrator.utils.decorators import web_help
from cosmotech.orchestrator.utils.logger import _format

LOGGER = logging.getLogger("csm.run.orchestrator.template_list")


def display_template(template, verbose=False):
    if verbose:
        LOGGER.info(pprint.pformat(template, width=os.get_terminal_size().columns))
    else:
        _desc = f": '{template.description}'" if template.description else ""
        LOGGER.info(f"- '{template.id}'{_desc}")


@click.command()
@click.option("-t",
              "--template-id",
              "templates",
              multiple=True,
              default=[],
              type=str,
              help="A list of templates id to check for")
@click.option("-v",
              "--verbose",
              is_flag=True,
              default=False,
              help="Display full information on the resulting templates")
@web_help("commands/list_templates")
def main(templates, verbose):
    """Show a list of pre-available command templates"""
    logging.basicConfig(
        format=_format,
        force=True,
        datefmt="[%Y/%m/%d-%X]",
        handlers=[RichHandler(rich_tracebacks=True,
                              omit_repeated_times=False,
                              show_path=False,
                              show_time=False,
                              show_level=False,
                              markup=True)])
    LOGGER.setLevel(logging.INFO)
    l = Library()
    if not l.templates:
        LOGGER.warning("There is no available template to display")
        return
    if templates:
        for temp in templates:
            if _template := l.find_template_by_name(temp):
                display_template(_template, verbose=True)
            else:
                LOGGER.error(f"{temp} is not a valid template id")
    else:
        current_plugin = None
        for _template in l.templates:
            if _template.sourcePlugin != current_plugin:
                current_plugin = _template.sourcePlugin
                LOGGER.info(f"Templates from '{current_plugin}':")
            display_template(_template, verbose=verbose)

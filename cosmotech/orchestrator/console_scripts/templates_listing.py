# Copyright (C) - 2023 - 2024 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import logging
import os
import pprint

from rich.logging import RichHandler

from cosmotech.orchestrator.core.orchestrator import FileLoader
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
              help="A template id to check for, can be used multiple times")
@click.option("-f",
              "--file",
              "orchestration_file",
              type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
              help="An orchestration file to add to the library")
@click.option("-v",
              "--verbose",
              is_flag=True,
              default=False,
              help="Display full information on the resulting templates")
@web_help("commands/list_templates")
def main(templates, orchestration_file, verbose):
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
    if orchestration_file:
        FileLoader(orchestration_file)()
    l = Library()
    if not l.templates:
        LOGGER.warning("There is no available template to display")
        return
    if templates:
        for temp in templates:
            l.display_template_by_id(temp, log_function=LOGGER.info, verbose=True)
    else:
        l.display_library(log_function=LOGGER.info, verbose=verbose)

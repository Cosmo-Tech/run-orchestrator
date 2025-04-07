# Copyright (C) - 2023 - 2025 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import click_log

from cosmotech.orchestrator import VERSION
from cosmotech.csm_orc.entrypoint import entrypoint_command
from cosmotech.csm_orc.run import run_command
from cosmotech.csm_orc.list_templates import list_templates_command
from cosmotech.orchestrator.utils.click import click
from cosmotech.orchestrator.utils.decorators import web_help
from cosmotech.orchestrator.utils.logger import LOGGER


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(f"CosmoTech Run Orchestrator {VERSION}")
    ctx.exit()


@click.group("csm-orc")
@click_log.simple_verbosity_option(LOGGER, "--log-level", envvar="LOG_LEVEL", show_envvar=True)
@web_help(None)
@click.option(
    "--version",
    is_flag=True,
    callback=print_version,
    expose_value=False,
    is_eager=True,
    help="Print version number and return.",
)
def main():
    """Cosmotech Run Orchestrator

    Command toolkit allowing to run Cosmotech Run Templates"""
    pass


main.add_command(entrypoint_command, "entrypoint")
main.add_command(run_command, "run")
main.add_command(list_templates_command, "list-templates")

if __name__ == "__main__":
    main()

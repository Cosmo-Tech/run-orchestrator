# Copyright (C) - 2023 - 2024 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from cosmotech.orchestrator.utils.click import click
from cosmotech.orchestrator.utils.decorators import web_help
from cosmotech.orchestrator.utils.logger import LOGGER


@click.command("fetch-run-data", deprecated=True)
@click.option("--organization-id",
              envvar="CSM_ORGANIZATION_ID",
              show_envvar=True,
              help="The id of an organization in the cosmotech api",
              metavar="o-##########")
@click.option("--workspace-id",
              envvar="CSM_WORKSPACE_ID",
              show_envvar=True,
              help="The id of a workspace in the cosmotech api",
              metavar="w-##########")
@click.option("--runner-id",
              envvar="CSM_RUNNER_ID",
              show_envvar=True,
              help="The id of a runner in the cosmotech api",
              metavar="s-##########")
@click.option("--parameters-absolute-path",
              envvar="CSM_PARAMETERS_ABSOLUTE_PATH",
              metavar="PATH",
              show_envvar=True,
              help="A local folder to store the parameters content")
@web_help("commands/scenario_data_downloader")
def main(
    **kwargs
):
    """
Download a runner data from the Cosmo Tech API
Requires a valid Azure connection either with:
- The AZ cli command: **az login**
- A triplet of env var `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`
    """
    LOGGER.error("""Command as been removed from csm-orc since [cyan bold]1.3.0[/]
You can find the new command in Cosmotech_Acceleration_Library version [cyan bold]0.7.0+[/]
Use [cyan bold]csm-data api run-load-data[/] instead
""")
    raise click.Abort("Command as been removed from csm-orc")


if __name__ == "__main__":
    main()

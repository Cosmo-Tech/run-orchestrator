# Copyright (C) - 2023 - 2024 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from cosmotech.orchestrator.utils.click import click
from cosmotech.orchestrator.utils.decorators import web_help
from cosmotech.orchestrator.utils.logger import LOGGER


@click.command("fetch-scenariorun-data", deprecated=True)
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
@click.option("--scenario-id",
              envvar="CSM_SCENARIO_ID",
              show_envvar=True,
              help="The id of a scenario in the cosmotech api",
              metavar="s-##########")
@click.option("--dataset-absolute-path",
              envvar="CSM_DATASET_ABSOLUTE_PATH",
              show_envvar=True,
              help="A local folder to store the main dataset content",
              metavar="PATH")
@click.option("--parameters-absolute-path",
              envvar="CSM_PARAMETERS_ABSOLUTE_PATH",
              metavar="PATH",
              show_envvar=True,
              help="A local folder to store the parameters content")
@click.option("--write-json/--no-write-json",
              envvar="WRITE_JSON",
              show_envvar=True,
              default=False,
              show_default=True,
              help="Toggle writing of parameters in json format")
@click.option("--write-csv/--no-write-csv",
              envvar="WRITE_CSV",
              show_envvar=True,
              default=True,
              show_default=True,
              help="Toggle writing of parameters in csv format")
@click.option("--fetch-dataset/--no-fetch-dataset",
              envvar="FETCH_DATASET",
              show_envvar=True,
              default=True,
              show_default=True,
              help="Toggle fetching datasets")
@click.option("--parallel/--no-parallel",
              envvar="FETCH_DATASETS_IN_PARALLEL",
              show_envvar=True,
              default=True,
              show_default=True,
              help="Toggle parallelization while fetching datasets,")
@web_help("commands/scenario_data_downloader")
def main(
    **kwargs
):
    """
Uses environment variables to call the download_scenario_data function
Requires a valid Azure connection either with:
- The AZ cli command: **az login**
- A triplet of env var `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`
    """
    LOGGER.error("""Command as been removed from csm-orc since [cyan bold]1.3.0[/]
You can find the new command in Cosmotech_Acceleration_Library version [cyan bold]0.7.0+[/]
Use [cyan bold]csm-data api scenariorun-load-data[/] instead
""")
    raise click.Abort("Command as been removed from csm-orc")


if __name__ == "__main__":
    main()

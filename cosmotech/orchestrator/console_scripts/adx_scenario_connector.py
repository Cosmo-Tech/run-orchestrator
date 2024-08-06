# Copyright (C) - 2023 - 2024 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from cosmotech.orchestrator.utils.click import click
from cosmotech.orchestrator.utils.decorators import web_help
from cosmotech.orchestrator.utils.logger import LOGGER


@click.command("send-to-adx",deprecated=True)
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
@click.option("--simulation-id",
              envvar="CSM_SIMULATION_ID",
              show_envvar=True,
              metavar="UUID",
              help="the Simulation Id to add to records")
@click.option("--adx-uri",
              envvar="AZURE_DATA_EXPLORER_RESOURCE_URI",
              show_envvar=True,
              metavar="URI",
              help="the ADX cluster path (URI info can be found into ADX cluster page)")
@click.option("--adx-ingest-uri",
              envvar="AZURE_DATA_EXPLORER_RESOURCE_INGEST_URI",
              show_envvar=True,
              metavar="URI",
              help="The ADX cluster ingest path (URI info can be found into ADX cluster page)")
@click.option("--database-name",
              envvar="AZURE_DATA_EXPLORER_DATABASE_NAME",
              show_envvar=True,
              metavar="NAME",
              help="The targeted database name")
@click.option("--send-parameters/--no-send-parameters",
              type=bool,
              envvar="CSM_SEND_DATAWAREHOUSE_PARAMETERS",
              show_envvar=True,
              show_default=True,
              help="whether or not to send parameters (parameters path is mandatory then)")
@click.option("--send-datasets/--no-send-datasets",
              type=bool,
              envvar="CSM_SEND_DATAWAREHOUSE_DATASETS",
              show_envvar=True,
              default=False,
              show_default=True,
              help="whether or not to send datasets (parameters path is mandatory then)")
@click.option("--wait/--no-wait",
              envvar="WAIT_FOR_INGESTION",
              show_envvar=True,
              default=False,
              show_default=True,
              help="Toggle waiting for the ingestion results")
@web_help("commands/simulation_to_adx")
def main(
    **kwargs
):
    """
Uses environment variables to send content of CSV files to ADX
Requires a valid Azure connection either with:
- The AZ cli command: **az login**
- A triplet of env var `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`
    """
    LOGGER.error("""Command as been removed from csm-orc since [cyan bold]1.3.0[/]
You can find the new command in Cosmotech_Acceleration_Library version [cyan bold]0.7.0+[/]
Use [cyan bold]csm-data adx-send-scenariodata[/] instead
""")
    raise click.Abort("Command as been removed from csm-orc")


if __name__ == "__main__":
    main()

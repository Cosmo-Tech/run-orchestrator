# Copyright (C) - 2023 - 2024 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from cosmotech.orchestrator.utils.click import click
from cosmotech.orchestrator.utils.decorators import web_help
from cosmotech.orchestrator.utils.logger import LOGGER


@click.group(deprecated=True)
@web_help("commands/parameters_generator")
def main():
    """Base command to initialize parameter folders  
Will create:    
- A `parameters.json`/`parameters.csv` in the folder with all parameters  
- A folder per `%DATASETID%` datasets with the name of the parameter  
Check the help of the sub commands for more information:  
- `cloud` requires access to a fully deployed solution  
- `solution` requires a `Solution.yaml` file"""
    pass


@main.command(deprecated=True)
@click.argument("solution_file",
                type=click.Path(file_okay=True, dir_okay=False, readable=True, writable=True),
                required=True,
                nargs=1)
@click.argument("output_folder",
                type=click.Path(dir_okay=True, readable=True, writable=True),
                required=True,
                envvar="CSM_PARAMETERS_ABSOLUTE_PATH",
                nargs=1)
@click.argument("run_template_id",
                required=True)
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
@web_help("commands/parameters_generator")
def solution(
    **kwargs
):
    """Initialize parameter folder for given run template from a Solution yaml file"""
    LOGGER.error("""Command as been removed from csm-orc since [cyan bold]1.3.0[/]
You can find the new command in Cosmotech_Acceleration_Library version [cyan bold]0.7.0+[/]
Use [cyan bold]csm-data legacy init-local-parameter-folder from-file[/] instead
""")
    raise click.Abort("Command as been removed from csm-orc")


@main.command(deprecated=True)
@click.argument("output_folder",
                envvar="CSM_PARAMETERS_ABSOLUTE_PATH",
                type=click.Path(dir_okay=True, readable=True, writable=True),
                required=True,
                nargs=1)
@click.option("--api-url",
              envvar="CSM_API_URL",
              show_envvar=True,
              help="The url to a Cosmotech API",
              metavar="URL",
              required=True)
@click.option("--api-scope",
              envvar="CSM_API_SCOPE",
              show_envvar=True,
              help="The identification scope of a Cosmotech API",
              metavar="URI",
              required=True)
@click.option("--organization-id",
              envvar="CSM_ORGANIZATION_ID",
              show_envvar=True,
              help="The id of an organization in the cosmotech api",
              metavar="o-##########",
              required=True)
@click.option("--workspace-id",
              envvar="CSM_WORKSPACE_ID",
              show_envvar=True,
              help="The id of a solution in the cosmotech api",
              metavar="w-##########",
              required=True)
@click.option("--run-template-id",
              envvar="CSM_RUN_TEMPLATE_ID",
              show_envvar=True,
              help="The name of the run template in the cosmotech api",
              metavar="NAME",
              required=True)
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
@web_help("commands/parameters_generator")
def cloud(
    **kwargs
):
    """Initialize parameter folder for given run template from CosmoTech cloud API"""
    LOGGER.error("""Command as been removed from csm-orc since [cyan bold]1.3.0[/]
You can find the new command in Cosmotech_Acceleration_Library version [cyan bold]0.7.0+[/]
Use [cyan bold]csm-data legacy init-local-parameter-folder from-api[/] instead
""")
    raise click.Abort("Command as been removed from csm-orc")


if __name__ == "__main__":
    main()

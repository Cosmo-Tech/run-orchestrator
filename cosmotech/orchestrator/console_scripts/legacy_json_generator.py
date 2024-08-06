# Copyright (C) - 2023 - 2024 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from cosmotech.orchestrator.utils.click import click
from cosmotech.orchestrator.utils.decorators import web_help
from cosmotech.orchestrator.utils.logger import LOGGER


@click.group("gen-from-legacy", deprecated=True)
@web_help("commands/legacy_json_generator")
def main():
    """Base command for the json generator using legacy files  
Check the help of the sub commands for more information:  
- `cloud` requires access to a fully deployed solution  
- `solution` requires a `Solution.yaml` file"""
    pass


@main.command("solution", deprecated=True)
@click.argument("solution_file",
                type=click.Path(file_okay=True, dir_okay=False, readable=True, writable=True),
                required=True,
                nargs=1)
@click.argument("output",
                type=click.Path(file_okay=True, dir_okay=False, readable=True, writable=True),
                required=True,
                nargs=1)
@click.argument("run-template-id",
                required=True)
@click.option("--describe/--no-describe",
              show_default=True, default=False,
              help="Show a description of the generated template after generation")
@web_help("commands/legacy_json_generator")
def solution(**kwargs):
    """Read SOLUTION_FILE to get a RUN_TEMPLATE_ID and generate an orchestrator file at OUTPUT"""
    LOGGER.error("""Command as been removed from csm-orc since [cyan bold]1.3.0[/]
You can find the new command in Cosmotech_Acceleration_Library version [cyan bold]0.7.0+[/]
Use [cyan bold]csm-data legacy generate-orchestrator from-file[/] instead
""")
    raise click.Abort("Command as been removed from csm-orc")


@main.command("cloud", deprecated=True)
@click.argument("output",
                type=click.Path(file_okay=True, dir_okay=False, readable=True, writable=True),
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
@click.option("--describe/--no-describe",
              show_default=True, default=False,
              help="Show a description of the generated template after generation")
@web_help("commands/legacy_json_generator")
def cloud(**kwargs):
    """Connect to the cosmotech API to download a run template and generate an orchestrator file at OUTPUT"""
    LOGGER.error("""Command as been removed from csm-orc since [cyan bold]1.3.0[/]
You can find the new command in Cosmotech_Acceleration_Library version [cyan bold]0.7.0+[/]
Use [cyan bold]csm-data legacy generate-orchestrator from-api[/] instead
""")
    raise click.Abort("Command as been removed from csm-orc")


if __name__ == "__main__":
    main()

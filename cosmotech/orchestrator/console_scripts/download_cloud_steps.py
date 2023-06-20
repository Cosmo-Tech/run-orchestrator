# Copyright (c) Cosmo Tech corporation.
# Licensed under the MIT license.
import logging

import click_log
import rich_click as click
from rich.logging import RichHandler
import cosmotech_api
from azure.identity import DefaultAzureCredential
from cosmotech_api.api.solution_api import SolutionApi
from cosmotech_api.api.workspace_api import WorkspaceApi, Workspace
from cosmotech_api.exceptions import ServiceException
import pathlib
from zipfile import ZipFile

click.rich_click.USE_MARKDOWN = True
LOGGER = logging.getLogger("scenario_data_downloader")
logging.basicConfig(
    format="%(message)s",
    datefmt="[%Y/%m/%d-%X]",
    handlers=[RichHandler(rich_tracebacks=True,
                          omit_repeated_times=False,
                          show_path=False,
                          markup=True)])
LOGGER.setLevel(logging.INFO)


@click.command()
@click_log.simple_verbosity_option(LOGGER,
                                   "--log-level",
                                   envvar="LOG_LEVEL",
                                   show_envvar=True)
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
@click.option("--handler-list",
              envvar="CSM_CONTAINER_MODE",
              show_envvar=True,
              help="A list of handlers to download (comma separated)",
              metavar="HANDLER,...,HANDLER",
              required=True)
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
def main(workspace_id, organization_id, run_template_id, handler_list, api_scope, api_url):
    """
Uses environment variables to download cloud based Template steps
Requires a valid Azure connection either with:
- The AZ cli command: **az login**
- A triplet of env var `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`
    """
    credentials = DefaultAzureCredential()
    token = credentials.get_token(api_scope)

    configuration = cosmotech_api.Configuration(
        host=api_url,
        discard_unknown_keys=True,
        access_token=token.token
    )
    LOGGER.info("Configuration to the api set")

    with cosmotech_api.ApiClient(configuration) as api_client:
        api_w = WorkspaceApi(api_client)

        LOGGER.info("Loading Workspace information to get Solution ID")
        try:
            r_data: Workspace = api_w.find_workspace_by_id(organization_id=organization_id, workspace_id=workspace_id)
        except ServiceException:
            LOGGER.error(f"Workspace [green bold]{workspace_id}[/] was not found "
                         f"in Organization [green bold]{organization_id}[/]")
            return 1
        solution_id = r_data.solution.solution_id

        api_sol = SolutionApi(api_client)
        handler_list = handler_list.replace("handle-parameters", "parameters_handler")
        root_path = pathlib.Path(".")
        template_path = root_path / run_template_id
        for handler_id in handler_list.split(','):
            handler_path: pathlib.Path = template_path / handler_id
            LOGGER.info(f"Querying Handler [green bold]{handler_id}[/] for [green bold]{run_template_id}[/]")
            try:
                r_data = api_sol.download_run_template_handler(organization_id=organization_id,
                                                               solution_id=solution_id,
                                                               run_template_id=run_template_id,
                                                               handler_id=handler_id)
            except ServiceException:
                LOGGER.error(
                    f"Handler [green bold]{handler_id}[/] was not found "
                    f"for Run Template [green bold]{run_template_id}[/] "
                    f"in Solution [green bold]{solution_id}[/]")
                continue
            LOGGER.info(f"Extracting handler to {handler_path.absolute()}")
            handler_path.mkdir(parents=True, exist_ok=True)

            with ZipFile(r_data) as _zip:
                _zip.extractall(handler_path)


if __name__ == "__main__":
    main()

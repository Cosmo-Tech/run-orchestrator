import json
import pathlib

import click_log
import cosmotech_api
import yaml
from azure.identity import DefaultAzureCredential
from cosmotech_api.api.solution_api import RunTemplate
from cosmotech_api.api.solution_api import Solution
from cosmotech_api.api.solution_api import SolutionApi
from cosmotech_api.api.workspace_api import Workspace
from cosmotech_api.api.workspace_api import WorkspaceApi
from cosmotech_api.exceptions import ServiceException

from cosmotech.orchestrator.classes import CustomJSONEncoder
from cosmotech.orchestrator.classes import Orchestrator
from cosmotech.orchestrator.classes import Step
from cosmotech.orchestrator.utils.click import click
from cosmotech.orchestrator.utils.logger import LOGGER


@click.group()
@click_log.simple_verbosity_option(LOGGER,
                                   "--log-level",
                                   envvar="LOG_LEVEL",
                                   show_envvar=True)
def main():
    """Base command for the json generator using legacy files  
Check the help of the sub commands for more information:  
- `cloud` requires access to a fully deployed solution  
- `solution` requires a `Solution.yaml` file"""
    pass


@main.command()
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
def solution(solution_file, run_template_id, output, describe):
    """Read SOLUTION_FILE to get a RUN_TEMPLATE_ID and generate an orchestrator file at OUTPUT"""
    solution_path = pathlib.Path(solution_file)
    if not solution_path.suffix == ".yaml":
        LOGGER.error(f"{solution_file} is not a `.yaml` file")
        return 1
    with solution_path.open() as _sf:
        solution_yaml = yaml.safe_load(_sf)
    LOGGER.info(f"Loaded {solution_path.absolute()}")
    _solution = Solution(_configuration=cosmotech_api.Configuration(discard_unknown_keys=True),
                         _spec_property_naming=True,
                         **solution_yaml)
    LOGGER.debug(json.dumps(_solution.to_dict(), indent=2))
    return generate_from_solution(sol=_solution, run_template_id=run_template_id, output=output, describe=describe)


@main.command()
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
def cloud(workspace_id, organization_id, run_template_id, api_scope, api_url, output, describe):
    """Connect to the cosmotech API to download a run template and generate an orchestrator file at OUTPUT"""
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
        except ServiceException as e:
            LOGGER.error(f"Workspace [green bold]{workspace_id}[/] was not found "
                         f"in Organization [green bold]{organization_id}[/]")
            LOGGER.debug(e.body)
            return 1
        solution_id = r_data.solution.solution_id

        api_sol = SolutionApi(api_client)
        sol: Solution = api_sol.find_solution_by_id(organization_id=organization_id, solution_id=solution_id)
        return generate_from_solution(sol=sol, run_template_id=run_template_id, output=output, describe=describe)


def generate_from_solution(sol: Solution, run_template_id, output: str, describe: bool = False):
    LOGGER.info(f"Searching [green bold]{run_template_id}[/] in the solution")
    if _t := [t for t in sol.run_templates if t.id == run_template_id]:
        template: RunTemplate = _t[0]
    else:
        LOGGER.error(f"Run template [green bold]{run_template_id}[/] was not found.")
        return 1
    LOGGER.info(f"Found [green bold]{run_template_id}[/] in the solution generating json file")
    generate_from_template(template, output)
    if describe:
        f = Orchestrator()
        c, s, g = f.load_json_file(output, False, True)
        LOGGER.debug(g)
        for k, v in s.items():
            LOGGER.info(v[0])


def generate_from_template(template: RunTemplate, output: str):
    steps = []
    previous = None
    if template.fetch_datasets is not False or template.fetch_scenario_parameters:
        LOGGER.info("- [green]fetch_scenario_parameters[/] step found")
        _s = Step(id="fetch_scenario_parameters",
                  command="cosmotech_scenario_downloader",
                  environment={
                      "CSM_ORGANIZATION_ID": {
                          "description": "The id of an organization in the cosmotech api"
                      },
                      "CSM_WORKSPACE_ID": {
                          "description": "The id of a workspace in the cosmotech api"
                      },
                      "CSM_SCENARIO_ID": {
                          "description": "The id of a scenario in the cosmotech api"
                      },
                      "CSM_API_URL": {
                          "description": "The url to a Cosmotech API"
                      },
                      "CSM_API_SCOPE": {
                          "description": "The identification scope of a Cosmotech API"
                      },
                      "CSM_DATASET_ABSOLUTE_PATH": {
                          "description": "A local folder to store the main dataset content"
                      },
                      "CSM_PARAMETERS_ABSOLUTE_PATH": {
                          "description": "A local folder to store the parameters content"
                      },
                      "WRITE_JSON": {
                          "description": "Toggle writing of parameters in json format",
                          "defaultValue": json.dumps(
                              template.fetch_scenario_parameters and template.parameters_json)
                      },
                      "WRITE_CSV": {
                          "description": "Toggle writing of parameters in csv format",
                          "defaultValue": json.dumps(
                              template.fetch_scenario_parameters and not template.parameters_json)
                      },
                      "FETCH_DATASET": {
                          "description": "Toggle fetching datasets",
                          "defaultValue": json.dumps(
                              template.fetch_dataset if template.fetch_dataset is not None else True)
                      },
                      "LOG_LEVEL": {
                          "description": "Either CRITICAL, ERROR, WARNING, INFO or DEBUG",
                          "defaultValue": "INFO"
                      },
                  })
        previous = "fetch_scenario_parameters"
        steps.append(_s)

    def run_template_phase(name, condition, source, _previous, default):
        _steps = []
        template_is_active = template.get(condition) if template.get(condition) is not None else default
        if template_is_active:
            if template.get(source) == "cloud":
                LOGGER.info(f"- [green]{name}_cloud[/] step found")
                _name = f"{name}_cloud"
                _step_dl_cloud = Step(id=_name,
                                      command="cosmotech_download_cloud_steps",
                                      environment={
                                          "CSM_ORGANIZATION_ID": {
                                              "description": "The id of an organization in the cosmotech api"
                                          },
                                          "CSM_WORKSPACE_ID": {
                                              "description": "The id of a workspace in the cosmotech api"
                                          },
                                          "CSM_RUN_TEMPLATE_ID": {
                                              "description": "The name of the run template in the cosmotech api",
                                              "defaultValue": template.id
                                          },
                                          "CSM_CONTAINER_MODE": {
                                              "description": "A list of handlers to download (comma separated)",
                                              "defaultValue": name
                                          },
                                          "CSM_API_URL": {
                                              "description": "The url to a Cosmotech API"
                                          },
                                          "CSM_API_SCOPE": {
                                              "description": "The identification scope of a Cosmotech API"
                                          },
                                          "AZURE_TENANT_ID": {
                                              "description": "An Azure Tenant ID"
                                          },
                                          "AZURE_CLIENT_ID": {
                                              "description": "An Azure Client ID having access to the Cosmotech API"
                                          },
                                          "AZURE_CLIENT_SECRET": {
                                              "description": "The secret for the Azure Client"
                                          },
                                          "LOG_LEVEL": {
                                              "description": "Either CRITICAL, ERROR, WARNING, INFO or DEBUG",
                                              "defaultValue": "INFO"
                                          },
                                      },
                                      )
                if _previous:
                    _step_dl_cloud.precedents = [_previous]
                _previous = _name
                _steps.append(_step_dl_cloud)
            LOGGER.info(f"- [green]{name}[/] step found")
            _run_step = Step(id=name,
                             command="cosmotech_run_step",
                             environment={
                                 "CSM_ORGANIZATION_ID": {
                                     "description": "The id of an organization in the cosmotech api"
                                 },
                                 "CSM_WORKSPACE_ID": {
                                     "description": "The id of a workspace in the cosmotech api"
                                 },
                                 "CSM_RUN_TEMPLATE_ID": {
                                     "description": "The name of the run template in the cosmotech api",
                                     "defaultValue": template.id
                                 },
                                 "CSM_CONTAINER_MODE": {
                                     "description": "A list of handlers to download (comma separated)",
                                     "defaultValue": name
                                 },
                                 "CSM_API_URL": {
                                     "description": "The url to a Cosmotech API"
                                 },
                                 "CSM_API_SCOPE": {
                                     "description": "The identification scope of a Cosmotech API"
                                 },
                                 "AZURE_TENANT_ID": {
                                     "description": "An Azure Tenant ID"
                                 },
                                 "AZURE_CLIENT_ID": {
                                     "description": "An Azure Client ID having access to the Cosmotech API"
                                 },
                                 "AZURE_CLIENT_SECRET": {
                                     "description": "The secret for the Azure Client"
                                 },
                                 "LOG_LEVEL": {
                                     "description": "Either CRITICAL, ERROR, WARNING, INFO or DEBUG",
                                     "defaultValue": "INFO"
                                 },
                                 "PYTHONPATH": {
                                     "description": "A list of folder to add to the python path",
                                     "defaultValue": ""
                                 },
                                 "CSM_DATASET_ABSOLUTE_PATH": {
                                     "description": "A local folder to store the main dataset content"
                                 },
                                 "CSM_PARAMETERS_ABSOLUTE_PATH": {
                                     "description": "A local folder to store the parameters content"
                                 },
                                 "CSM_SIMULATION_ID": {
                                     "description": "The id of the simulation run"
                                 },
                                 "CSM_SIMULATION": {
                                     "description": "The name of the Simulation file to use"
                                 },
                                 "AZURE_DATA_EXPLORER_RESOURCE_URI": {
                                     "description": "the ADX cluster path (URI info can be found into ADX cluster page)"
                                 },
                                 "AZURE_DATA_EXPLORER_RESOURCE_INGEST_URI": {
                                     "description": "The ADX cluster ingest path (URI info can be found into ADX cluster page)"
                                 },
                                 "AZURE_DATA_EXPLORER_DATABASE_NAME": {
                                     "description": "The targeted database name"
                                 },
                             })
            if template.csm_simulation is not None:
                _run_step.environment["CSM_SIMULATION"].defaultValue = template.csm_simulation
            if _previous:
                _run_step.precedents = [_previous]
            _previous = name
            _steps.append(_run_step)
        return _previous, _steps

    previous, new_steps = run_template_phase("parameters_handler", "apply_parameters", "parameters_handler_source",
                                             previous, False)
    steps.extend(new_steps)
    previous, new_steps = run_template_phase("validator", "validator", "validator_source", previous, False)
    steps.extend(new_steps)
    if template.send_datasets_to_data_warehouse is True or template.send_input_parameters_to_data_warehouse is True:
        LOGGER.info("- [green]send_to_adx[/] step found")
        _send_to_adx_step = Step(id="send_to_adx",
                                 command="cosmotech_simulation_to_adx_connector",
                                 environment={
                                     "AZURE_TENANT_ID": {
                                         "description": "An Azure Tenant ID"
                                     },
                                     "AZURE_CLIENT_ID": {
                                         "description": "An Azure Client ID having access to the Cosmotech API"
                                     },
                                     "AZURE_CLIENT_SECRET": {
                                         "description": "The secret for the Azure Client"
                                     },
                                     "LOG_LEVEL": {
                                         "description": "Either CRITICAL, ERROR, WARNING, INFO or DEBUG",
                                         "defaultValue": "INFO"
                                     },
                                     "CSM_DATASET_ABSOLUTE_PATH": {
                                         "description": "A local folder to store the main dataset content"
                                     },
                                     "CSM_PARAMETERS_ABSOLUTE_PATH": {
                                         "description": "A local folder to store the parameters content"
                                     },
                                     "CSM_SIMULATION_ID": {
                                         "description": "The id of the simulation run"
                                     },
                                     "AZURE_DATA_EXPLORER_RESOURCE_URI": {
                                         "description": "the ADX cluster path (URI info can be found into ADX cluster page)"
                                     },
                                     "AZURE_DATA_EXPLORER_RESOURCE_INGEST_URI": {
                                         "description": "The ADX cluster ingest path (URI info can be found into ADX cluster page)"
                                     },
                                     "AZURE_DATA_EXPLORER_DATABASE_NAME": {
                                         "description": "The targeted database name"
                                     },
                                     "CSM_SEND_DATAWAREHOUSE_PARAMETERS": {
                                         "description": "whether or not to send parameters (parameters path is mandatory then)",
                                         "defaultValue": json.dumps(
                                             template.send_input_parameters_to_data_warehouse is True)
                                     },
                                     "CSM_SEND_DATAWAREHOUSE_DATASETS": {
                                         "description": "whether or not to send datasets (parameters path is mandatory then)",
                                         "defaultValue": json.dumps(
                                             template.send_datasets_to_data_warehouse is True)
                                     },
                                     "WAIT_FOR_INGESTION": {
                                         "description": "Toggle waiting for the ingestion results",
                                         "defaultValue": "false"
                                     },
                                 })
    previous, new_steps = run_template_phase("prerun", "pre_run", "pre_run_source", previous, False)
    steps.extend(new_steps)
    previous, new_steps = run_template_phase("engine", "run", "run_source", previous, True)
    steps.extend(new_steps)
    previous, new_steps = run_template_phase("postrun", "post_run", "post_run_source", previous, False)
    steps.extend(new_steps)
    LOGGER.debug(json.dumps({"steps": steps}, cls=CustomJSONEncoder, indent=2))
    LOGGER.info(f"{len(steps)} step{'s' if len(steps) > 1 else ''} found, writing json file")
    json.dump({"steps": steps}, open(output, "w"), cls=CustomJSONEncoder, indent=2)


if __name__ == "__main__":
    main()
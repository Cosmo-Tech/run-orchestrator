# Copyright (c) Cosmo Tech corporation.
# Licensed under the MIT license.
import json
import logging
import os
import pathlib
from distutils.dir_util import copy_tree

import click_log
import rich_click as click
from CosmoTech_Acceleration_Library.Accelerators.scenario_download.scenario_downloader import ScenarioDownloader
from rich.logging import RichHandler

from cosmotech.orchestrator.utils.decorators import require_env

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


def download_scenario_data(
    organization_id: str, workspace_id: str, scenario_id: str, dataset_folder: str, parameter_folder: str
) -> None:
    """
    Download the datas from a scenario from the CosmoTech API to the local file system
    :param scenario_id: The id of the Scenario as defined in the CosmoTech API
    :param organization_id: The id of the Organization as defined in the CosmoTech API
    :param workspace_id: The id of the Workspace as defined in the CosmoTech API
    :param dataset_folder: a local folder where the main dataset of the scenario will be downloaded
    :param parameter_folder: a local folder where all parameters will be downloaded
    :return: Nothing
    """
    LOGGER.info("Starting connector")
    dl = ScenarioDownloader(workspace_id=workspace_id,
                            organization_id=organization_id,
                            read_files=False)
    LOGGER.info("Initialized downloader")
    content = dict()
    content['datasets'] = dl.get_all_datasets(scenario_id=scenario_id)

    content['parameters'] = dl.get_all_parameters(scenario_id=scenario_id)
    LOGGER.info("Downloaded content")
    dataset_paths = dict()

    dataset_dir = dataset_folder

    for k in content['datasets'].keys():
        dataset_paths[k] = dl.dataset_to_file(k, content['datasets'][k])
        if k not in content['parameters'].values():
            copy_tree(dataset_paths[k], dataset_dir)

    LOGGER.info("Stored datasets")
    tmp_parameter_dir = parameter_folder

    tmp_parameter_file = os.path.join(tmp_parameter_dir, "parameters.json")

    parameters = []

    for parameter_name, value in content['parameters'].items():
        def add_file_parameter(compared_parameter_name: str, dataset_id: str):
            if parameter_name == compared_parameter_name:
                param_dir = os.path.join(tmp_parameter_dir, compared_parameter_name)
                pathlib.Path(param_dir).mkdir(exist_ok=True)
                dataset_content_path = dataset_paths[dataset_id]
                copy_tree(dataset_content_path, param_dir)
                parameters.append({
                    "parameterId": parameter_name,
                    "value": parameter_name,
                    "varType": "%DATASETID%"
                })

        if value in content['datasets']:
            add_file_parameter(parameter_name, value)
        parameters.append({
            "parameterId": parameter_name,
            "value": value,
            "varType": str(type(value).__name__)
        })

    with open(tmp_parameter_file, "w") as _file:
        json.dump(parameters, _file)
    LOGGER.info("Generated parameters.json")


@click.command()
@click.option("--organization-id",
              envvar="CSM_ORGANIZATION_ID",
              show_envvar=True,
              help="The id of an organization in the cosmotech api",
              metavar="o-##########",
              required=True)
@click.option("--workspace-id",
              envvar="CSM_WORKSPACE_ID",
              show_envvar=True,
              help="The id of a workspace in the cosmotech api",
              metavar="w-##########",
              required=True)
@click.option("--scenario-id",
              envvar="CSM_SCENARIO_ID",
              show_envvar=True,
              help="The id of a scenario in the cosmotech api",
              metavar="s-##########",
              required=True)
@click.option("--dataset-absolute-path",
              envvar="CSM_DATASET_ABSOLUTE_PATH",
              show_envvar=True,
              help="A local folder to store the main dataset content",
              metavar="PATH",
              required=True)
@click.option("--parameters-absolute-path",
              envvar="CSM_PARAMETERS_ABSOLUTE_PATH",
              metavar="PATH",
              show_envvar=True,
              help="A local folder to store the parameters content",
              required=True)
@click_log.simple_verbosity_option(LOGGER,
                                   "--log-level",
                                   envvar="LOG_LEVEL",
                                   show_envvar=True)
@require_env('CSM_API_SCOPE', "The identification scope of a Cosmotech API")
@require_env('CSM_API_URL', "The URL to a Cosmotech API")
def main(
    scenario_id: str, workspace_id: str, organization_id: str, dataset_absolute_path: str, parameters_absolute_path: str
):
    """
Uses environment variables to call the download_scenario_data function
Requires a valid Azure connection either with:
- The AZ cli command: **az login**
- A triplet of env var `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`
    """
    download_scenario_data(organization_id, workspace_id, scenario_id, dataset_absolute_path, parameters_absolute_path)


if __name__ == "__main__":
    main()

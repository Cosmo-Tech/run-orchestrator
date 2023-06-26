# Copyright (c) Cosmo Tech corporation.
# Licensed under the MIT license.
import json
import logging
import os
import pathlib
from csv import DictWriter
from distutils.dir_util import copy_tree

import click_log
import rich_click as click
from CosmoTech_Acceleration_Library.Accelerators.scenario_download.scenario_downloader import ScenarioDownloader
from rich.console import Console
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
    organization_id: str,
    workspace_id: str,
    scenario_id: str,
    dataset_folder: str,
    parameter_folder: str,
    write_json: bool,
    write_csv: bool
) -> None:
    """
    Download the datas from a scenario from the CosmoTech API to the local file system
    :param scenario_id: The id of the Scenario as defined in the CosmoTech API
    :param organization_id: The id of the Organization as defined in the CosmoTech API
    :param workspace_id: The id of the Workspace as defined in the CosmoTech API
    :param dataset_folder: a local folder where the main dataset of the scenario will be downloaded
    :param parameter_folder: a local folder where all parameters will be downloaded
    :param write_json: should parameters be written as json file
    :param write_csv: should parameters be written as csv file
    :return: Nothing
    """
    LOGGER.info("Starting connector")
    dl = ScenarioDownloader(workspace_id=workspace_id,
                            organization_id=organization_id,
                            read_files=False)

    LOGGER.info("Load scenario data")
    scenario_data = dl.get_scenario_data(scenario_id=scenario_id)
    LOGGER.info("Download datasets")
    datasets = dl.get_all_datasets(scenario_id=scenario_id)
    datasets_parameters_ids = {param.get('value'): param.get('parameter_id')
                               for param in scenario_data.get('parameters_values')
                               if param.get('var_type') == "%DATASETID%"}

    dataset_dir = dataset_folder
    tmp_parameter_dir = parameter_folder

    LOGGER.info("Store datasets")
    pathlib.Path(dataset_dir).mkdir(parents=True, exist_ok=True)
    for k in datasets.keys():
        if k in scenario_data.get('dataset_list', ()):
            copy_tree(dl.dataset_to_file(k, datasets[k]), dataset_dir)
            LOGGER.debug(f"  - [yellow]{dataset_dir}[/] ([green]{k}[/])")
        if k in datasets_parameters_ids.keys():
            param_dir = os.path.join(tmp_parameter_dir, datasets_parameters_ids[k])
            pathlib.Path(param_dir).mkdir(exist_ok=True, parents=True)
            copy_tree(dl.dataset_to_file(k, datasets[k]), param_dir)
            LOGGER.debug(f"  - [yellow]{datasets_parameters_ids[k]}[/] ([green]{k}[/])")

    pathlib.Path(tmp_parameter_dir).mkdir(parents=True, exist_ok=True)

    LOGGER.info("Prepare parameters")

    if not (write_csv or write_json):
        LOGGER.info("No parameters write asked, skipping")
        return

    parameters = []
    max_name_size = max(map(lambda r: len(r.get('parameter_id')), scenario_data['parameters_values']))
    max_type_size = max(map(lambda r: len(r.get('var_type')), scenario_data['parameters_values']))
    for parameter_data in scenario_data['parameters_values']:
        parameter_name = parameter_data.get('parameter_id')
        value = parameter_data.get('value')
        var_type = parameter_data.get('var_type')
        is_inherited = parameter_data.get('is_inherited')
        parameters.append({
            "parameterId": parameter_name,
            "value": value,
            "varType": var_type,
            "isInherited": is_inherited
        })
        LOGGER.debug(f"  - [yellow]{parameter_name:<{max_name_size}}[/] [cyan]{var_type:<{max_type_size}}[/] "
                     f"\"{value}\"{' [red bold]inherited[/]' if is_inherited else ''}")

    if write_csv:
        tmp_parameter_file = os.path.join(tmp_parameter_dir, "parameters.csv")
        LOGGER.info(f"Generating {tmp_parameter_file}")
        with open(tmp_parameter_file, "w") as _file:
            _w = DictWriter(_file, fieldnames=["parameterId", "value", "varType", "isInherited"])
            _w.writeheader()
            _w.writerows(parameters)

    if write_json:
        tmp_parameter_file = os.path.join(tmp_parameter_dir, "parameters.json")
        LOGGER.info(f"Generating {tmp_parameter_file}")
        with open(tmp_parameter_file, "w") as _file:
            json.dump(parameters, _file)


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
@click.option("--write-json/--no-write-json",
              envvar="WRITE_JSON",
              show_envvar=True,
              default=False,
              help="Toggle writing of parameters in json format")
@click.option("--write-csv/--no-write-csv",
              envvar="WRITE_CSV",
              show_envvar=True,
              default=True,
              help="Toggle writing of parameters in csv format")
@click_log.simple_verbosity_option(LOGGER,
                                   "--log-level",
                                   envvar="LOG_LEVEL",
                                   show_envvar=True)
@require_env('CSM_API_SCOPE', "The identification scope of a Cosmotech API")
@require_env('CSM_API_URL', "The URL to a Cosmotech API")
def main(
    scenario_id: str,
    workspace_id: str,
    organization_id: str,
    dataset_absolute_path: str,
    parameters_absolute_path: str,
    write_json: bool,
    write_csv: bool
):
    """
Uses environment variables to call the download_scenario_data function
Requires a valid Azure connection either with:
- The AZ cli command: **az login**
- A triplet of env var `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`
    """
    return download_scenario_data(organization_id, workspace_id, scenario_id, dataset_absolute_path,
                                  parameters_absolute_path, write_json, write_csv)


if __name__ == "__main__":
    main()

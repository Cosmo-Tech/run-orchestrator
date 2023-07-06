# Copyright (C) - 2023 - 2023 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import json
import pathlib
from typing import Optional

import cosmotech_api
import yaml
from azure.identity import DefaultAzureCredential
from cosmotech_api.api.solution_api import Solution
from cosmotech_api.api.solution_api import SolutionApi
from cosmotech_api.api.workspace_api import Workspace
from cosmotech_api.api.workspace_api import WorkspaceApi
from cosmotech_api.exceptions import ServiceException

from cosmotech.orchestrator.utils.logger import LOGGER


def read_solution_file(solution_file) -> Optional[Solution]:
    solution_path = pathlib.Path(solution_file)
    if not solution_path.suffix == ".yaml":
        LOGGER.error(f"{solution_file} is not a `.yaml` file")
        return None
    with solution_path.open() as _sf:
        solution_yaml = yaml.safe_load(_sf)
    LOGGER.info(f"Loaded {solution_path.absolute()}")
    _solution = Solution(_configuration=cosmotech_api.Configuration(discard_unknown_keys=True),
                         _spec_property_naming=True,
                         **solution_yaml)
    LOGGER.debug(json.dumps(_solution.to_dict(), indent=2))
    return _solution


def get_solution(api_scope, api_url, organization_id, workspace_id) -> Optional[Solution]:
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
            return None
        solution_id = r_data.solution.solution_id

        api_sol = SolutionApi(api_client)
        sol: Solution = api_sol.find_solution_by_id(organization_id=organization_id, solution_id=solution_id)
    return sol

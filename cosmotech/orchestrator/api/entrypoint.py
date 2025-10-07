# Copyright (C) - 2023 - 2025 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

"""
API functions for the Docker entrypoint.

This module provides functions that implement the core functionality of the
csm-orc entrypoint command, allowing them to be used directly without the CLI context.
"""

import configparser
import importlib.util
import logging
import os
import subprocess
from pathlib import Path
from shutil import which
from typing import Dict

import sys

from cosmotech.orchestrator.utils.translate import T

LOGGER = logging.getLogger("csm.run.entrypoint")
HANDLER = logging.StreamHandler(sys.stdout)
HANDLER.setFormatter(logging.Formatter("%(message)s"))
LOGGER.addHandler(HANDLER)
LOGGER.setLevel(logging.INFO)


class EntrypointException(Exception):
    """Exception raised for errors in the entrypoint."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


def get_entrypoint_env() -> Dict[str, str]:
    """
    Get environment variables from the project file.

    Returns:
        Dictionary of environment variables
    """
    LOGGER.debug(T("csm-orc.cli.entrypoint.context"))
    project_file = configparser.ConfigParser()
    project_file.read("/pkg/share/project.csm")

    env_vars = {}
    if project_file.has_section("EntrypointEnv"):
        for key, value in project_file.items("EntrypointEnv"):
            env_key = key.upper()
            os.environ.setdefault(env_key, value)
            env_vars[env_key] = value

    return env_vars


def get_simulator_executable_name() -> str:
    simulator_exe_name = "csm-simulator"
    # Check for old simulator name below SDK version 11.1.0
    old_main = "main"
    if which(simulator_exe_name) is None and which(old_main):
        return old_main
    return simulator_exe_name


def run_direct_simulator() -> int:
    """
    Run the simulator directly.

    Returns:
        Exit code from the simulator
    """
    if os.environ.get("CSM_SIMULATION"):
        LOGGER.info(T("csm-orc.cli.entrypoint.simulation.info").format(simulation=os.environ.get("CSM_SIMULATION")))

        args = ["-i", os.environ.get("CSM_SIMULATION")]
        if os.environ.get("CSM_PROBES_MEASURES_TOPIC") is not None:
            LOGGER.debug(
                T("csm-orc.cli.entrypoint.simulation.probes_topic").format(
                    topic=os.environ.get("CSM_PROBES_MEASURES_TOPIC")
                )
            )
            args = args + ["--amqp-consumer", os.environ.get("CSM_PROBES_MEASURES_TOPIC")]
        else:
            LOGGER.warning(T("csm-orc.cli.entrypoint.simulation.no_probes_topic"))

        if os.environ.get("CSM_CONTROL_PLANE_TOPIC") is not None:
            LOGGER.debug(
                T("csm-orc.cli.entrypoint.simulation.control_topic").format(
                    topic=os.environ.get("CSM_CONTROL_PLANE_TOPIC")
                )
            )
        else:
            LOGGER.warning(T("csm-orc.cli.entrypoint.simulation.no_control_topic"))
    else:
        # Check added for use of legacy entrypoint.py name - to be removed when legacy stack is removed
        if sys.argv[0].endswith("entrypoint.py"):
            args = sys.argv[1:]
        else:
            args = sys.argv[2:]
        LOGGER.debug(T("csm-orc.cli.entrypoint.simulation.args").format(args=args))

    try:
        return subprocess.check_call([get_simulator_executable_name()] + args)
    except subprocess.CalledProcessError as e:
        return e.returncode


def setup_loki_logging() -> None:
    """
    Set up logging to Loki if CSM_LOKI_URL is set in the environment.
    """
    if "CSM_LOKI_URL" in os.environ:
        import logging_loki

        handler = logging_loki.LokiHandler(
            url=os.environ.get("CSM_LOKI_URL", ""),
            tags={
                "organization_id": os.environ.get("CSM_ORGANIZATION_ID"),
                "workspace_id": os.environ.get("CSM_WORKSPACE_ID"),
                "runner_id": os.environ.get("CSM_RUNNER_ID"),
                "run_id": os.environ.get("CSM_RUN_ID"),
                "namespace": os.environ.get("CSM_NAMESPACE_NAME"),
                "container": os.environ.get("ARGO_CONTAINER_NAME"),
                "pod": os.environ.get("ARGO_NODE_ID"),
            },
            version="1",
        )
        handler.emitter.session.headers.setdefault("X-Scope-OrgId", os.environ.get("CSM_NAMESPACE_NAME", ""))
        LOGGER.addHandler(handler)


def run_template_with_id(template_id: str, project_root: Path = Path("/pkg/share")) -> int:
    """
    Run a template with the given ID.

    Args:
        template_id: ID of the template to run
        project_root: Root directory of the project

    Returns:
        Exit code from the template run
    """
    LOGGER.setLevel(logging.DEBUG)
    LOGGER.info(T("csm-orc.cli.entrypoint.start"))

    if importlib.util.find_spec("cosmotech") is None or importlib.util.find_spec("cosmotech.orchestrator") is None:
        raise EntrypointException(T("csm-orc.orchestrator.errors.missing_library"))

    orchestrator_json = project_root / "code/run_templates" / template_id / "run.json"
    if not orchestrator_json.is_file():
        raise EntrypointException(T("csm-orc.orchestrator.errors.no_run_json").format(template_id=template_id))

    _env = os.environ.copy()
    p = subprocess.Popen(
        ["csm-orc", "run", str(orchestrator_json.absolute())],
        cwd=project_root,
        env=_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    log_func = LOGGER.info
    for r in iter(p.stdout.readline, ""):
        _r = r.upper()
        if "WARN" in _r:
            log_func = LOGGER.warning
        elif "ERROR" in _r:
            log_func = LOGGER.error
        elif "DEBUG" in _r:
            log_func = LOGGER.debug
        elif "INFO" in _r:
            log_func = LOGGER.info
        log_func(r.strip())

    return_code = p.wait()
    return return_code


def get_project_path() -> Path:
    """
    Get the project path if it exists.

    Returns:
        The project path if it exists, otherwise the default path.
    """
    default_docker_path = Path("/pkg/share")
    current_folder = os.getcwd()
    project_csm_path = Path(current_folder) / "project.csm"
    return Path(current_folder) if project_csm_path.is_file() else default_docker_path


def run_entrypoint() -> int:
    """
    Run the Docker entrypoint logic.

    Returns:
        Exit code
    """
    try:
        setup_loki_logging()
        get_entrypoint_env()

        template_id = os.environ.get("CSM_RUN_TEMPLATE_ID")
        if template_id is None:
            LOGGER.debug(T("csm-orc.cli.entrypoint.simulation.no_template"))
            return run_direct_simulator()

        return run_template_with_id(template_id, project_root=get_project_path())

    except EntrypointException as e:
        LOGGER.error(e)
        return 1
    except subprocess.CalledProcessError:
        return 1

import configparser
import importlib.util
import logging
import os
import subprocess
from pathlib import Path
from shutil import which

import sys

from cosmotech.orchestrator.utils.click import click
from cosmotech.orchestrator.utils.logger import LOGGER


class EntrypointException(Exception):
    def __init__(self, message):
        self.message = message


def get_env():
    LOGGER.debug("Setting context from project.csm")
    project_file = configparser.ConfigParser()
    project_file.read("/pkg/share/project.csm")
    if project_file.has_section("EntrypointEnv"):
        for key, value in project_file.items("EntrypointEnv"):
            os.environ.setdefault(key.upper(), value)


def run_direct_simulator():
    if os.environ.get("CSM_SIMULATION"):
        LOGGER.info(f"Simulation: {os.environ.get('CSM_SIMULATION')}")

        args = ["-i", os.environ.get("CSM_SIMULATION")]
        if os.environ.get('CSM_PROBES_MEASURES_TOPIC') is not None:
            LOGGER.debug(f"Probes measures topic: {os.environ.get('CSM_PROBES_MEASURES_TOPIC')}")
            args = args + ["--amqp-consumer", os.environ.get('CSM_PROBES_MEASURES_TOPIC')]
        else:
            LOGGER.warning("No probes measures topic")

        if os.environ.get('CSM_CONTROL_PLANE_TOPIC') is not None:
            LOGGER.debug(f"Control plane topic: {os.environ.get('CSM_CONTROL_PLANE_TOPIC')}."
                         "Simulator binary is able to handle "
                         "CSM_CONTROL_PLANE_TOPIC directly so it is not "
                         "transformed as an argument.")
        else:
            LOGGER.warning("No Control plane topic")
    else:
        # Check added for use of legacy entrypoint.py name - to be removed when legacy stack is removed
        if "entrypoint.py" == sys.argv[0]:
            args = sys.argv[1:]
        else:
            args = sys.argv[2:]
        LOGGER.debug(f"Simulator arguments: {args}")

    simulator_exe_name = "csm-simulator"
    # Check for old simulator name below SDK version 11.1.0
    old_main = "main"
    if which(simulator_exe_name) is None and which(old_main):
        simulator_exe_name = old_main

    subprocess.check_call([simulator_exe_name] + args)


@click.command(hidden="True", context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
def main():
    """Docker entrypoint

    This command is used in CosmoTech docker containers only"""
    if "CSM_LOKI_URL" in os.environ:
        import logging_loki

        handler = logging_loki.LokiHandler(
            url=os.environ.get("CSM_LOKI_URL"),
            tags={
                "organization_id": os.environ.get("CSM_ORGANIZATION_ID"),
                "workspace_id": os.environ.get("CSM_WORKSPACE_ID"),
                "runner_id": os.environ.get("CSM_RUNNER_ID"),
                "run_id": os.environ.get("CSM_RUN_ID"),
                "namespace": os.environ.get("CSM_NAMESPACE_NAME"),
                "container": os.environ.get("ARGO_CONTAINER_NAME"),
                "pod": os.environ.get("ARGO_NODE_ID"),
            },
            version="1"
        )
        handler.emitter.session.headers.setdefault("X-Scope-OrgId", os.environ.get("CSM_NAMESPACE_NAME"))
        LOGGER.addHandler(handler)

    try:
        get_env()

        template_id = os.environ.get("CSM_RUN_TEMPLATE_ID")
        if template_id is None:
            LOGGER.debug("No run template id defined in environment variable \"CSM_RUN_TEMPLATE_ID\" "
                         "running direct simulator mode")
            run_direct_simulator()
            return
        LOGGER.setLevel(logging.DEBUG)
        LOGGER.info("Csm-orc Entry Point")
        if importlib.util.find_spec("cosmotech") is None or importlib.util.find_spec(
                "cosmotech.orchestrator") is None:
            raise EntrypointException(
                "You need to install the library `cosmotech-run-orchestrator` in your container. "
                "Check if you set it in your requirements.txt.")
        project_root = Path("/pkg/share")
        orchestrator_json = project_root / "code/run_templates" / template_id / "run.json"
        if not orchestrator_json.is_file():
            raise EntrypointException(f"No \"run.json\" defined for the run template {template_id}")
        _env = os.environ.copy()
        p = subprocess.Popen(["csm-orc", "run", str(orchestrator_json.absolute())],
                             cwd=project_root,
                             env=_env,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             text=True)
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
        if return_code != 0:
            raise click.Abort()

    except subprocess.CalledProcessError:
        raise click.Abort()


if __name__ == "__main__":
    main()

# Copyright (C) - 2023 - 2023 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import os
import pathlib
import subprocess
import sys
import venv

from cosmotech.orchestrator.utils.click import click
from cosmotech.orchestrator.utils.decorators import web_help
from cosmotech.orchestrator.utils.logger import LOGGER


@click.command()
@click.option("--template",
              envvar="CSM_RUN_TEMPLATE_ID",
              required=True,
              show_envvar=True,
              help="refer to a folder contained in `code/run_templates`")
@click.option("--steps",
              envvar="CSM_CONTAINER_MODE",
              default="CSMDOCKER",
              show_envvar=True,
              show_default=True,
              help="\bA list of Steps definer in the `TEMPLATE` folder that will be executed (comma-separated).  \n"
                   "Defaults to `CSMDOCKER` equivalent to "
                   "`parameters_handler,validator,prerun,engine,postrun` (the legacy order)")
@web_help("commands/run_step")
def main(template: str, steps: str):
    """Runs a list of steps of a run template in a CosmoTech project
Known limitations:
- The step MUST contain an executable main.py file
- The engine step requires to set the env var CSM_SIMULATION if you have a run without a python engine
- QT consumer in the simulator breaks the engine step when orchestrating
"""
    project = pathlib.Path(".")
    steps = steps.split(",")
    if not project.exists() or not (project / "project.csm").exists():
        LOGGER.error(f"{project} is not the root directory of a Cosmo project.")
        exit(1)
    error = executor(project, template, steps)
    exit(error)


def executor(project: pathlib.Path, template: str, steps: list[str]):
    LOGGER.debug(f"Project path: {project.absolute()}")
    template_list = list(
        str(l.relative_to(project / "code/run_templates")) for l in project.glob('code/run_templates/*'))
    target_template = next((s for s in template_list if s.lower() == template.lower()), None)
    if target_template is None:
        LOGGER.warning("Existing run templates")
        for t in template_list:
            LOGGER.warning(f"\t- {t}")
        return 1
    template_path = project / "code/run_templates" / target_template
    available_steps = list(template_path.glob('*'))
    csmdocker = False
    engine_possible_paths = [project / "Generated/Build/Bin/main", pathlib.Path("/pkg/bin/main")]
    engine_path = None
    if "CSMDOCKER" in steps:
        steps = ["parameters_handler", "validator", "prerun", "engine", "postrun"]
        csmdocker = True
    _steps = []
    for s in steps:
        if template_path / s in available_steps:
            if _steps is not None:
                _steps.append(s)
            continue
        if s == "engine":
            for possible_engine in engine_possible_paths:
                if possible_engine.exists():
                    engine_path = possible_engine
                    _steps.append(s)
                    break
            else:
                LOGGER.error('No engine exists for step "engine"')
                _steps = None
            continue
        if not csmdocker:
            LOGGER.error(f"{s} is not a valid step")
            _steps = None

    if not _steps:
        LOGGER.warning("Available steps")
        for s in available_steps:
            LOGGER.warning(f"\t- {s.name}")
        return 1

    for s in _steps:
        if s == "engine" and engine_path is not None:
            if not (simulation := os.environ.get('CSM_SIMULATION')):
                LOGGER.error("To use direct main simulation (no engine step in python) "
                             "you need to set the environment variable CSM_SIMULATION "
                             "with the name of the simulation file to be run")
            else:
                args = ["-i",
                        simulation]
                subprocess.run(args=args,
                               executable=str(engine_path.absolute()))
            continue
        main_path = template_path / s

        executable = sys.executable
        if (req_path := main_path / "requirements.txt").exists():
            LOGGER.info(f"Found {req_path}, setting a venv to install it")
            reqs = subprocess.check_output([executable, '-m', 'pip', 'freeze']).decode(sys.stdout.encoding).strip()
            venv_path = main_path / '.venv'
            if not venv_path.exists():
                venv.create(venv_path, with_pip=True)
            executable = str(venv_path / "bin/python")
            subprocess.run([executable, '-m', 'pip', 'install'] + reqs.split("\n"))
            subprocess.run([executable, '-m', 'pip', 'install', '-r', str(req_path)])

        LOGGER.info(f"Running {s} step")
        p = subprocess.run([executable, str(main_path.absolute() / "main.py")])
        if p.returncode != 0:
            LOGGER.error(f"Issue while running step {s} please check your logs")
            return 1
        LOGGER.debug(f"Finished running step {s}")

    else:
        LOGGER.info("Template run finished")
    return 0


if __name__ == "__main__":
    main()

import importlib.util
import logging
import os
import pathlib
import sys

import click_log
import rich_click as click
from rich.logging import RichHandler

click.rich_click.USE_MARKDOWN = True
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = False

LOGGER = logging.getLogger("csm_executor")
logging.basicConfig(
    format="%(message)s",
    datefmt="[%Y/%m/%d-%X]",
    handlers=[RichHandler(rich_tracebacks=True,
                          omit_repeated_times=False,
                          show_path=False,
                          markup=True)])
LOGGER.setLevel(logging.INFO)


@click.command()
@click.argument("template", nargs=1)
@click.argument("steps", nargs=-1)
@click_log.simple_verbosity_option(LOGGER,
                                   "--log-level",
                                   envvar="LOG_LEVEL",
                                   show_envvar=True)
def main(template, steps):
    """Runs a list of steps of a run template in a CosmoTech project

- `TEMPLATE` refer to a folder contained in `code/run_templates`
- `STEPS` is a list of Steps definer in the `TEMPLATE` folder that will be executed
    - defaults to `CSMDOCKER` which represent the legacy order: `parameters_handler` - `validator` - `prerun` - `engine` - `postrun`

Known limitations:
- The template MUST contain a main.py file with a main() function
- The engine step requires to set the env var CSM_SIMULATION if you have a run without a python engine
"""
    project = pathlib.Path(".")
    if not len(steps):
        steps = ["CSMDOCKER", ]
    if not project.exists() or not (project / "project.csm").exists():
        LOGGER.error(f"{project} is not the root directory of a Cosmo project.")
        return 1
    executor(project, template, steps)


def executor(project: pathlib.Path, template: str, steps: list[str]):
    LOGGER.debug(f"Project path: {project.absolute()}")
    template_list = list(
        str(l.relative_to(project / "code/run_templates")) for l in project.glob('code/run_templates/*'))
    target_template = next((s for s in template_list if s.lower() == template.lower()), None)
    if target_template is None:
        LOGGER.warning("Existing run templates")
        for t in template_list:
            LOGGER.warning(f"\t- {t}")
        return
    template_path = project / "code/run_templates" / target_template
    available_steps = list(template_path.glob('*'))
    csmdocker = False
    use_main_engine = False
    if "CSMDOCKER" in steps:
        steps = ["parameters_handler", "validator", "prerun", "engine", "postrun"]
        csmdocker = True
    _steps = []
    for s in steps:
        if template_path / s in available_steps:
            _steps.append(s)
            continue
        if s == "engine" and (project / "Generated/Build/Bin/main").exists():
            use_main_engine = True
            _steps.append(s)
            continue
        if not csmdocker:
            LOGGER.error(f"{s} is not a valid step")
            _steps = None

    if not _steps:
        LOGGER.warning("Available steps")
        for s in available_steps:
            LOGGER.warning(f"\t- {s.name}")
        return

    for s in _steps:
        if s == "engine" and use_main_engine:
            import subprocess
            if not (simulation := os.environ.get('CSM_SIMULATION')):
                LOGGER.error("To use direct main simulation (no engine step in python) "
                             "you need to set the environment variable CSM_SIMULATION "
                             "with the name of the simulation file to be run")
            else:
                subprocess.run(["-i", simulation],
                               executable="Generated/Build/Bin/main")
            continue
        main_path = template_path / s
        added_modules = []
        for py_file in main_path.glob('*.py'):
            n = py_file.name[:-3]
            if n == "main":
                continue
            LOGGER.debug(f"Loading {py_file} as {n}")
            _spec = importlib.util.spec_from_file_location(n, str(py_file.absolute().resolve()))
            _mod = importlib.util.module_from_spec(_spec)
            sys.modules[n] = _mod
            added_modules.append(n)
            _spec.loader.exec_module(_mod)

        spec = importlib.util.spec_from_file_location(f"runstep.{s}", str(main_path.absolute().resolve() / "main.py"))
        LOGGER.debug(f"Loading {main_path / 'main.py'} as 'runstep.{s}'")
        mainmod = importlib.util.module_from_spec(spec)
        sys.modules[f"runstep.{s}"] = mainmod
        spec.loader.exec_module(mainmod)
        LOGGER.debug(f"Running step {s}")
        try:
            mainmod.main()
        except SystemExit as e:
            LOGGER.error(f"Issue while running step {s} please check your logs")
            break
        LOGGER.debug(f"Finished running step {s}")
    else:
        LOGGER.info("Template run finished")


if __name__ == "__main__":
    main()

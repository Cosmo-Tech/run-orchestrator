# Copyright (C) - 2023 - 2023 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import pathlib
from typing import Optional

from cosmotech.orchestrator.core.orchestrator import Orchestrator
from cosmotech.orchestrator.utils.click import click
from cosmotech.orchestrator.utils.decorators import web_help
from cosmotech.orchestrator.utils.logger import LOGGER
from cosmotech.orchestrator import VERSION


@click.command()
@click.argument("template", type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True), nargs=1)
@click.option("--dry-run/--no-dry-run", "-n",
              envvar="DRY_RUN",
              show_envvar=True,
              default=False,
              show_default=True,
              help="Use dry-run mode")
@click.option("--display-env/--no-display-env",
              envvar="DISPLAY_ENVIRONMENT",
              show_envvar=True,
              default=False,
              show_default=True,
              help="List all required environment variables and their documentation")
@click.option("--gen-env-target",
              envvar="GENERATE_ENVIRONMENT",
              show_envvar=True,
              default=None,
              show_default=True,
              type=click.Path(),
              help="Generate a .env file with all env vars to be filed when display-env is called")
@click.option("--skip-step", "skipped_steps",
              envvar="CSM_SKIP_STEPS",
              show_envvar=True,
              default=[],
              type=str,
              multiple=True,
              metavar="STEP_ID",
              help="Define a list of steps to be skipped during this run")
@click.option("--validate-only/--no-validate-only", "validate_only",
              envvar="CSM_ORCHESTRATOR_VALIDATE_ONLY",
              show_envvar=True,
              default=False,
              help="Run only a sematic validation of the orchestrator file")
@web_help("commands/orchestrator")
def main(template: str, dry_run: bool, display_env: bool, gen_env_target: Optional[str], skipped_steps: list[str], 
         validate_only: bool):
    """Runs the given `TEMPLATE` file  
Commands are run as subprocess using `bash -c "<command> <arguments>"`.  
In case you are in a python venv, the venv is activated before any command is run."""
    LOGGER.info(f"Starting run orchestrator version {VERSION}")
    f = Orchestrator()
    try:
        c, s, g = f.load_json_file(template, dry_run, display_env, skipped_steps, validate_only)
    except ValueError as e:
        LOGGER.error(e)
    else:
        if g is None:
            return
        if not display_env:
            LOGGER.info("===      Run     ===")
            g.evaluate(mode="threading")
            LOGGER.info("===     Results    ===")
            LOGGER.debug(g)
            for k, v in s.items():
                LOGGER.info(v[0])
        elif gen_env_target is not None:
            _fp = pathlib.Path(gen_env_target)
            _fp.parent.mkdir(parents=True, exist_ok=True)
            with _fp.open("w") as _f:
                _env: dict[str, str] = dict()
                _env.update(
                    {k: v.description if v.effective_value() is None else v.effective_value() for _s, _ in s.values()
                     for k, v in _s.environment.items()})
                _f.writelines(f"{k}=\"{v}\"\n" for k, v in sorted(_env.items(), key=lambda e: e[0]))


if __name__ == "__main__":
    main()

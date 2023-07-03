import pathlib
from typing import Optional

import click_log

from cosmotech.orchestrator.classes import Orchestrator
from cosmotech.orchestrator.utils.click import click
from cosmotech.orchestrator.utils.logger import LOGGER


@click.command()
@click.argument("template", type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True), nargs=1)
@click_log.simple_verbosity_option(LOGGER,
                                   "--log-level",
                                   envvar="LOG_LEVEL",
                                   show_envvar=True)
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
              help="Generate a .env file with all env vars to be filed when display-env is called")
def main(template: str, dry_run: bool, display_env: bool, gen_env_target: Optional[str]):
    """Runs the given TEMPLATE file  
Commands are run as subprocess using `bash -c "<command> <arguments>"`.  
In case you are in a python venv, the venv is activated before any command is run."""
    f = Orchestrator()
    try:
        c, s, g = f.load_json_file(template, dry_run, display_env)
    except ValueError as e:
        LOGGER.error(e)
    else:
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

from cosmotech.orchestrator.classes import Orchestrator

import click_log
import rich_click as click

from cosmotech.orchestrator.utils.logger import LOGGER


@click.command()
@click.argument("template", type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True), nargs=1)
@click_log.simple_verbosity_option(LOGGER,
                                   "--log-level",
                                   envvar="LOG_LEVEL",
                                   show_envvar=True)
@click.option("-n", "--dry-run/--no-dry-run",
              envvar="DRY_RUN",
              show_envvar=True,
              default=False,
              help="Use dry-run mode")
@click.option("--display-env/--no-display-env",
              envvar="DISPLAY_ENVIRONMENT",
              show_envvar=True,
              default=False,
              help="List all required environment variables and their documentation")
def main(template: str, dry_run: bool, display_env: bool):
    """Runs the given TEMPLATE file"""
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


if __name__ == "__main__":
    main()

# Copyright (C) - 2023 - 2025 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from typing import Optional

from cosmotech.orchestrator import VERSION
from cosmotech.orchestrator.api.run import run_template, validate_template, display_environment, generate_env_file
from cosmotech.orchestrator.utils.click import click
from cosmotech.orchestrator.utils.decorators import web_help
from cosmotech.orchestrator.utils.logger import LOGGER
from cosmotech.orchestrator.utils.translate import T


@click.command()
@click.argument("template", type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True), nargs=1)
@click.option(
    "--dry-run/--no-dry-run",
    "-n",
    envvar="DRY_RUN",
    show_envvar=True,
    default=False,
    show_default=True,
    help="Use dry-run mode",
)
@click.option(
    "--display-env/--no-display-env",
    envvar="DISPLAY_ENVIRONMENT",
    show_envvar=True,
    default=False,
    show_default=True,
    help="List all required environment variables and their documentation",
)
@click.option(
    "--gen-env-target",
    envvar="GENERATE_ENVIRONMENT",
    show_envvar=True,
    default=None,
    show_default=True,
    type=click.Path(),
    help="Generate a .env file with all env vars to be filed when display-env is called",
)
@click.option(
    "--skip-step",
    "skipped_steps",
    envvar="CSM_SKIP_STEPS",
    show_envvar=True,
    default=[],
    type=str,
    multiple=True,
    metavar="STEP_ID",
    help="Define a list of steps to be skipped during this run",
)
@click.option(
    "--validate-only/--no-validate-only",
    "validate_only",
    envvar="CSM_ORCHESTRATOR_VALIDATE_ONLY",
    show_envvar=True,
    default=False,
    show_default=True,
    help="Run only a sematic validation of the orchestrator file",
)
@click.option(
    "--exit-handlers/--no-exit-handlers",
    "exit_handlers",
    envvar="CSM_ORCHESTRATOR_USE_EXIT_HANDLERS",
    show_envvar=True,
    default=True,
    show_default=True,
    help="Run exit handlers at the end of the execution",
)
@web_help("commands/orchestrator")
def run_command(
    template: str,
    dry_run: bool,
    display_env: bool,
    gen_env_target: Optional[str],
    skipped_steps: list[str],
    validate_only: bool,
    exit_handlers: bool,
):
    """Runs the given `TEMPLATE` file
    Commands are run as subprocess using `bash -c "<command> <arguments>"`.
    In case you are in a python venv, the venv is activated before any command is run."""

    # Handle validate-only mode
    if validate_only:
        if not validate_template(template):
            raise click.Abort()
        return

    # Handle display-env mode
    if display_env or gen_env_target:
        try:
            if gen_env_target:
                generate_env_file(template, gen_env_target)
            else:
                display_environment(template)
            return
        except ValueError as e:
            LOGGER.error(str(e))
            raise click.Abort()

    # Run the template
    success, _ = run_template(
        template_path=template,
        dry_run=dry_run,
        display_env=display_env,
        skipped_steps=skipped_steps,
        exit_handlers=exit_handlers,
    )

    if not success:
        raise click.Abort()


if __name__ == "__main__":
    run_command()

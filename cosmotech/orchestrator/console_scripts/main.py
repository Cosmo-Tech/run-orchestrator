# Copyright (C) - 2023 - 2023 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import click_log

from cosmotech.orchestrator import VERSION
from cosmotech.orchestrator.console_scripts.adx_scenario_connector import main as adx_cmd
from cosmotech.orchestrator.console_scripts.download_cloud_steps import main as dl_cloud_cmd
from cosmotech.orchestrator.console_scripts.entrypoint import main as entrypoint_cmd
from cosmotech.orchestrator.console_scripts.legacy_json_generator import main as legacy_gen_cmd
from cosmotech.orchestrator.console_scripts.run import main as run_cmd
from cosmotech.orchestrator.console_scripts.parameters_generation import main as parameters_cmd
from cosmotech.orchestrator.console_scripts.run_step import main as run_step_cmd
from cosmotech.orchestrator.console_scripts.scenario_data_downloader import main as scenario_dl_cmd
from cosmotech.orchestrator.utils.click import click
from cosmotech.orchestrator.utils.decorators import web_help
from cosmotech.orchestrator.utils.logger import LOGGER


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(f"CosmoTech Run Orchestrator {VERSION}")
    ctx.exit()


@click.group("csm-orc")
@click_log.simple_verbosity_option(LOGGER,
                                   "--log-level",
                                   envvar="LOG_LEVEL",
                                   show_envvar=True)
@web_help(None)
@click.option('--version',
              is_flag=True,
              callback=print_version,
              expose_value=False,
              is_eager=True,
              help="Print version number and return.")
def main():
    """Cosmotech Run Orchestrator
    
Command toolkit allowing to run Cosmotech Run Templates"""
    pass


main.add_command(adx_cmd, "send-to-adx")
main.add_command(dl_cloud_cmd, "fetch-cloud-steps")
main.add_command(entrypoint_cmd, "entrypoint")
main.add_command(legacy_gen_cmd, "gen-from-legacy")
main.add_command(run_cmd, "run")
main.add_command(parameters_cmd, "init-parameters")
main.add_command(run_step_cmd, "run-step")
main.add_command(scenario_dl_cmd, "fetch-scenariorun-data")

if __name__ == "__main__":
    main()

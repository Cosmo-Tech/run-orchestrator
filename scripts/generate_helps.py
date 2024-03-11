# Copyright (C) - 2023 - 2023 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import contextlib
import io
import pathlib
import re

import click

from cosmotech.orchestrator.console_scripts.adx_scenario_connector import main as adx_scenario_connector_command
from cosmotech.orchestrator.console_scripts.download_cloud_steps import main as dl_cloud_steps_command
from cosmotech.orchestrator.console_scripts.legacy_json_generator import cloud as legacy_gen_command_cloud
from cosmotech.orchestrator.console_scripts.legacy_json_generator import main as legacy_gen_command
from cosmotech.orchestrator.console_scripts.legacy_json_generator import solution as legacy_gen_command_sol
from cosmotech.orchestrator.console_scripts.parameters_generation import cloud as parameters_generation_command_cloud
from cosmotech.orchestrator.console_scripts.parameters_generation import main as parameters_generation_command
from cosmotech.orchestrator.console_scripts.parameters_generation import solution as parameters_generation_command_sol
from cosmotech.orchestrator.console_scripts.run import main as orchestrator_run_command
from cosmotech.orchestrator.console_scripts.run_step import main as run_step_command
from cosmotech.orchestrator.console_scripts.runner_data_downloader import main as runner_dl_command
from cosmotech.orchestrator.console_scripts.scenario_data_downloader import main as scenario_data_dl_command
from cosmotech.orchestrator.console_scripts.templates_listing import main as list_tpl_command

ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
commands = {
    "csm-orc run-step": run_step_command,
    "csm-orc fetch-cloud-steps": dl_cloud_steps_command,
    "csm-orc fetch-run-data": runner_dl_command,
    "csm-orc fetch-scenariorun-data": scenario_data_dl_command,
    "csm-orc send-to-adx": adx_scenario_connector_command,
    "csm-orc run": orchestrator_run_command,
    "csm-orc gen-from-legacy": legacy_gen_command,
    "csm-orc gen-from-legacy solution": legacy_gen_command_sol,
    "csm-orc gen-from-legacy cloud": legacy_gen_command_cloud,
    "csm-orc init-parameters": parameters_generation_command,
    "csm-orc init-parameters solution": parameters_generation_command_sol,
    "csm-orc init-parameters cloud": parameters_generation_command_cloud,
    "csm-orc list-templates": list_tpl_command,
}
help_folder = pathlib.Path("generated/commands_help")
help_folder.mkdir(parents=True, exist_ok=True)
for command, cmd in commands.items():
    with open(f"generated/commands_help/{command}.txt".replace(" ", "_"), "w") as _md_file:
        _md_file.write(f"> {command} --help\n")
        f = io.StringIO()
        with click.Context(cmd, info_name=command) as ctx:
            with contextlib.redirect_stdout(f):
                cmd.get_help(ctx)
        f.seek(0)
        o = ansi_escape.sub('', "".join(f.readlines()))
        _md_file.write(o)

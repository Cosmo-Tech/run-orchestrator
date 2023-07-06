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
from cosmotech.orchestrator.console_scripts.orchestrator import main as orchestrator_command
from cosmotech.orchestrator.console_scripts.run_step import main as run_step_command
from cosmotech.orchestrator.console_scripts.scenario_data_downloader import main as scenario_data_dl_command
from cosmotech.orchestrator.console_scripts.parameters_generation import cloud as parameters_generation_command_cloud
from cosmotech.orchestrator.console_scripts.parameters_generation import main as parameters_generation_command
from cosmotech.orchestrator.console_scripts.parameters_generation import solution as parameters_generation_command_sol

ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
commands = {
    "cosmotech_run_step": run_step_command,
    "cosmotech_download_cloud_steps": dl_cloud_steps_command,
    "cosmotech_scenario_downloader": scenario_data_dl_command,
    "cosmotech_simulation_to_adx_connector": adx_scenario_connector_command,
    "cosmotech_orchestrator": orchestrator_command,
    "cosmotech_gen_legacy": legacy_gen_command,
    "cosmotech_gen_legacy solution": legacy_gen_command_sol,
    "cosmotech_gen_legacy cloud": legacy_gen_command_cloud,
    "cosmotech_init_parameters": parameters_generation_command,
    "cosmotech_init_parameters solution": parameters_generation_command_sol,
    "cosmotech_init_parameters cloud": parameters_generation_command_cloud
}
help_folder = pathlib.Path("docs/scripts_help")
help_folder.mkdir(parents=True, exist_ok=True)
for command, cmd in commands.items():
    with open(f"docs/scripts_help/{command}.txt".replace(" ", "_"), "w") as _md_file:
        _md_file.write(f"> {command} --help\n")
        f = io.StringIO()
        with click.Context(cmd, info_name=command) as ctx:
            with contextlib.redirect_stdout(f):
                cmd.get_help(ctx)
        f.seek(0)
        o = ansi_escape.sub('', "".join(f.readlines()))
        _md_file.write(o)
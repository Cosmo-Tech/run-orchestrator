import contextlib
import io
import pathlib
import re

import click

from cosmotech.orchestrator.console_scripts.adx_scenario_connector import main as adx_scenario_connector_command
from cosmotech.orchestrator.console_scripts.download_cloud_steps import main as dl_cloud_steps_command
from cosmotech.orchestrator.console_scripts.run_step import main as run_step_command
from cosmotech.orchestrator.console_scripts.scenario_data_downloader import main as scenario_data_dl_command
from cosmotech.orchestrator.console_scripts.orchestrator import main as orchestrator_command

ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
commands = {
    "cosmotech_run_step": run_step_command,
    "cosmotech_download_cloud_steps": dl_cloud_steps_command,
    "cosmotech_scenario_downloader": scenario_data_dl_command,
    "cosmotech_simulation_to_adx_connector": adx_scenario_connector_command,
    "cosmotech_orchestrator": orchestrator_command,
}
help_folder = pathlib.Path("docs/scripts_help")
help_folder.mkdir(parents=True, exist_ok=True)
for command, cmd in commands.items():
    with open(f"docs/scripts_help/{command}.txt", "w") as _md_file:
        _md_file.write(f"> {command} --help\n")
        f = io.StringIO()
        with click.Context(cmd, info_name=command) as ctx:
            with contextlib.redirect_stdout(f):
                cmd.get_help(ctx)
        f.seek(0)
        o = ansi_escape.sub('', "".join(f.readlines()))
        _md_file.write(o)

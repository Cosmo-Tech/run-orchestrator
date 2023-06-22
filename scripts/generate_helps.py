import os
import pathlib
import re
import subprocess
import shutil

ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')

commands = ["cosmotech_run_step",
            "cosmotech_download_cloud_steps",
            "cosmotech_scenario_downloader",
            "cosmotech_simulation_to_adx_connector", ]
help_folder = pathlib.Path("docs/scripts_help")
help_folder.mkdir(parents=True, exist_ok=True)
size = 120
try:
    size = os.get_terminal_size().columns
    os.system("stty cols 120")
except OSError:
    pass
for command in commands:
    with open(f"docs/scripts_help/{command}.txt", "w") as _md_file:
        _md_file.write(f"> {command} --help\n")
        o = ansi_escape.sub("", subprocess.check_output([command, "--help"], encoding='UTF-8').strip())
        _md_file.write(o)
try:
    os.system(f"mode con cols={size}")
except OSError:
    pass

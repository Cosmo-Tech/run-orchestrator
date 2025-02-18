# Copyright (C) - 2023 - 2024 - Cosmo Tech
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

from cosmotech.orchestrator.console_scripts.run import main as orchestrator_run_command
from cosmotech.orchestrator.console_scripts.templates_listing import main as list_tpl_command

ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
commands = {
    "csm-orc run": orchestrator_run_command,
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

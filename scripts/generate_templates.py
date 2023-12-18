# Copyright (C) - 2023 - 2023 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import pathlib
import re
from string import Template

import mkdocs_gen_files

from cosmotech.orchestrator.templates.library import Library
from cosmotech.orchestrator.core.command_template import CommandTemplate

ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')

library = Library()


def gen_doc(template: CommandTemplate):
    env_content = "\n    ".join(e.name + " | " + (e.description or "None") for e in template.environment.values())
    env = f"""
    Variable Name | Description
    ------------- | -----------
    {env_content}
"""
    ret = {
        "id": template.id,
        "description": template.description or "",
        "command": template.command,
        "arguments": ' '.join(template.arguments),
        "env": env if template.environment else "",
        "has_desc": "" if template.description else "hidden",
        "has_env": "" if template.environment else "hidden",
    }
    return ret


for _template in library.templates:
    with mkdocs_gen_files.open(f"command_templates/{_template.sourcePlugin}/{_template.id}.md", "w") as _md_file, \
            open("scripts/command_template.template.md") as tpl_file:
        _tpl = Template(tpl_file.read())
        _md_file.write(_tpl.safe_substitute(gen_doc(_template)))

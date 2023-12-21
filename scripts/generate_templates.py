# Copyright (C) - 2023 - 2023 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import json
from string import Template

import mkdocs_gen_files

from cosmotech.orchestrator.core.command_template import CommandTemplate
from cosmotech.orchestrator.templates.library import Library

library = Library()


def gen_doc(template: CommandTemplate):
    env_content = "\n    ".join(e.name
                                + ("  :material-tag-hidden:{ title=\"optional\"}" if e.optional else "")
                                + " | "
                                + (e.description or "None")
                                for e in template.environment.values())
    env = f"""
    Variable Name | Description
    ------------- | -----------
    {env_content}
"""
    json_content = json.dumps(template.serialize(), indent=2, separators=(',', ':'))
    json_content = "\n".join(map(lambda _line: f"    {_line}", json_content.split("\n")))
    ret = {
        "id": template.id,
        "description": template.description or "",
        "command": template.command,
        "arguments": ' '.join(template.arguments),
        "env": env if template.environment else "",
        "use_sys_env": "" if template.useSystemEnvironment else "hidden",
        "has_desc": "" if template.description else "hidden",
        "has_env": "" if template.environment else "hidden",
        "json_content": json_content,
    }
    return ret


for _template in library.templates:
    with mkdocs_gen_files.open(f"command_templates/"
                               f"{_template.sourcePlugin}/"
                               f"{_template.id.replace(' ', '_')}.md", "w") as _md_file, \
            open("scripts/command_template.template.md") as tpl_file:
        _tpl = Template(tpl_file.read())
        _md_file.write(_tpl.safe_substitute(gen_doc(_template)))

# Copyright (C) - 2023 - 2023 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import pathlib
import re

import mkdocs_gen_files

from cosmotech.orchestrator.templates.library import Library
from cosmotech.orchestrator.core.command_template import CommandTemplate

ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')

library = Library()


def gen_doc(template: CommandTemplate):
    title = f"# {template.id}"
    description = f"Description: {template.description}"
    command_line = f"Command: {template.command} {' '.join(template.arguments)}"
    env_content = "\n    ".join(e.name + " | " + (e.description or "None") for e in template.environment.values())
    env = f"""???+ info "Environment"
    Variable Name | Description
    ------------- | -----------
    {env_content}
"""

    doc_page = [title]
    if template.description:
        doc_page.extend(("\n", description))
    doc_page.extend(("\n", command_line))
    if template.environment:
        doc_page.extend(("\n", env))
    return "\n".join(doc_page)


for _template in library.templates:
    with mkdocs_gen_files.open(f"command_templates/{_template.sourcePlugin}/{_template.id}.md", "w") as _md_file:
        _md_file.write(gen_doc(_template))

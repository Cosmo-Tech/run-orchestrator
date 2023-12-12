# Copyright (C) - 2023 - 2023 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import pathlib
import re

from cosmotech.orchestrator.templates.library import Library

ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')

library = Library()

for template in library.templates:
    help_folder = pathlib.Path(f"docs/command_templates/{template.sourcePlugin}")
    help_folder.mkdir(parents=True, exist_ok=True)
    with open(f"docs/command_templates/{template.sourcePlugin}/{template.id}.md", "w") as _md_file:
        _md_file.write(template.gen_doc())

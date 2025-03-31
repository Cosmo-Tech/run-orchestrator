# Copyright (C) - 2023 - 2024 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from string import Template
from typing import IO

import mkdocs_gen_files

from cosmotech.orchestrator import VERSION

_md_file: IO
with mkdocs_gen_files.open("index.md", "w") as _md_file, open("scripts/index.template.md") as index_template, open(
    "README.md"
) as readme:
    _index: list[str] = index_template.readlines()
    _readme_content = readme.readlines()
    for _line in _index:
        _tpl = Template(_line)
        _md_file.write(_tpl.safe_substitute({"version": VERSION}))

# Copyright (C) - 2023 - 2023 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from typing import IO

import mkdocs_gen_files

from cosmotech.orchestrator import VERSION

_md_file: IO
with mkdocs_gen_files.open("index.md", "w") as _md_file, \
        open("scripts/index.template.md") as index_template, \
        open("README.md") as readme:
    _index: list[str] = index_template.readlines()
    _readme_content = readme.readlines()
    for _line in _index:
        if "--README--" in _line:
            _md_file.writelines(_readme_content[1:])
            continue
        _md_file.write(_line.replace("%%VERSION%%", VERSION))

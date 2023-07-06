# Copyright (C) - 2023 - 2023 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import json

from cosmotech.orchestrator.core.command_template import CommandTemplate
from cosmotech.orchestrator.core.environment import EnvironmentVariable
from cosmotech.orchestrator.core.step import Step


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Step) or isinstance(o, CommandTemplate) or isinstance(o, EnvironmentVariable):
            return o.serialize()
        return json.JSONEncoder.default(self, o)

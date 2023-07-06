import json

from cosmotech.orchestrator.core.command_template import CommandTemplate
from cosmotech.orchestrator.core.environment import EnvironmentVariable
from cosmotech.orchestrator.core.step import Step


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Step) or isinstance(o, CommandTemplate) or isinstance(o, EnvironmentVariable):
            return o.serialize()
        return json.JSONEncoder.default(self, o)

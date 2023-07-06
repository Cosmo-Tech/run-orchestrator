from dataclasses import dataclass
from dataclasses import field
from typing import Union

from cosmotech.orchestrator.core.environment import EnvironmentVariable


@dataclass
class CommandTemplate:
    id: str = field()
    command: str = field()
    arguments: list[str] = field(default_factory=list)
    environment: dict[str, Union[EnvironmentVariable, dict]] = field(default_factory=dict)

    def __post_init__(self):
        tmp_env = dict()
        for k, v in self.environment.items():
            tmp_env[k] = EnvironmentVariable(k, **v)
        self.environment = tmp_env

    def serialize(self):
        r = {
            "id": self.id,
        }
        if self.command:
            r["command"] = self.command
        if self.arguments:
            r["arguments"] = self.arguments
        if self.environment:
            r["environment"] = self.environment
        return r

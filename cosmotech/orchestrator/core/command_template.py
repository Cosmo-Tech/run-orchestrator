# Copyright (C) - 2023 - 2023 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from dataclasses import dataclass
from dataclasses import field
from typing import Union

from cosmotech.orchestrator.core.environment import EnvironmentVariable


@dataclass
class CommandTemplate:
    id: str = field()
    command: str = field()
    description: str = field(default=None)
    arguments: list[str] = field(default_factory=list)
    environment: dict[str, Union[EnvironmentVariable, dict]] = field(default_factory=dict)
    useSystemEnvironment: bool = field(default=False)

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
        if self.description:
            r["description"] = self.description
        if self.useSystemEnvironment:
            r["useSystemEnvironment"] = self.useSystemEnvironment
        return r

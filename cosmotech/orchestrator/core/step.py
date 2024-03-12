# Copyright (C) - 2023 - 2023 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import os
import pathlib
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from dataclasses import field
from typing import Union

from cosmotech.orchestrator.core.command_template import CommandTemplate
from cosmotech.orchestrator.core.environment import EnvironmentVariable
from cosmotech.orchestrator.templates.library import Library
from cosmotech.orchestrator.utils.logger import LOGGER


@dataclass
class Step:
    id: str = field()
    commandId: str = field(default=None)
    command: str = field(default=None)
    description: str = field(default=None)
    arguments: list[str] = field(default_factory=list)
    environment: dict[str, Union[EnvironmentVariable, dict]] = field(default_factory=dict)
    precedents: list[Union[str, 'Step']] = field(default_factory=list)
    useSystemEnvironment: bool = field(default=False)
    loaded = False
    status = None
    skipped = False

    def __load_command_from_library(self):
        library = Library()
        if not self.commandId or self.loaded:
            LOGGER.debug(f"[green bold]{self.id}[/] already ready")
            return
        command: CommandTemplate = library.find_template_by_name(self.commandId)
        if command is None:
            self.status = "Error"
            LOGGER.error(f"[green bold]{self.id}[/] asks for a non existing template [cyan bold]{self.commandId}[/]")
            raise ValueError(f"Command Template {self.commandId} is not available")
        LOGGER.debug(f"[green bold]{self.id}[/] loads template [cyan bold]{self.commandId}[/]")
        self.command = command.command
        self.arguments = command.arguments[:] + self.arguments
        self.useSystemEnvironment = self.useSystemEnvironment or command.useSystemEnvironment
        if self.description is None:
            self.description = command.description
        for _env_key, _env in command.environment.items():
            if _env_key in self.environment:
                self.environment[_env_key].join(_env)
            else:
                self.environment[_env_key] = _env

    def __post_init__(self):
        if not bool(self.command) ^ bool(self.commandId):
            self.status = "Error"
            raise ValueError("A step requires either a command or a commandId")
        tmp_env = dict()
        for k, v in self.environment.items():
            tmp_env[k] = EnvironmentVariable(k, **v)
        self.environment = tmp_env
        self.status = "Init"
        if self.commandId:
            self.__load_command_from_library()
        self.loaded = True

    def serialize(self):
        r = {
            "id": self.id,
        }
        if self.command:
            r["command"] = self.command
        if self.commandId:
            r["commandId"] = self.commandId
        if self.arguments:
            r["arguments"] = self.arguments
        if self.environment:
            r["environment"] = self.environment
        if self.precedents:
            r["precedents"] = self.precedents
        if self.description:
            r["description"] = self.description
        if self.useSystemEnvironment:
            r["useSystemEnvironment"] = self.useSystemEnvironment
        return r

    def _effective_env(self):
        _env = dict()
        for k, v in self.environment.items():
            _v = v.effective_value()
            if _v is None:
                if v.optional:
                    break
                _v = ""
            _env[k] = _v
        # Special case for "PATH" EnvVar due to subprocess run method
        # to avoid needing to add "UseSystemEnv" in every step
        if "PATH" not in _env and os.environ.get("PATH"):
            _env["PATH"] = os.environ.get("PATH")
        return _env

    def run(self, dry: bool = False, previous=None):
        if previous is None:
            previous = dict()

        LOGGER.info(f"Starting step [green bold]{self.id}[/]")
        self.status = "Ready"
        if isinstance(previous, dict) and any(map(lambda a: a not in ['Done', 'DryRun'], previous.values())):
            LOGGER.warning(f"Skipping step [green bold]{self.id}[/] due to previous errors")
            self.status = "Skipped"
        if self.status == "Ready":
            if self.skipped:
                LOGGER.info(f"Skipping step [green bold]{self.id}[/] as required")
                self.status = "Done"
            elif dry:
                self.status = "DryRun"
            else:
                _e = self._effective_env()
                if self.useSystemEnvironment:
                    _e = {**os.environ, **_e}
                try:
                    executable = pathlib.Path(sys.executable)
                    venv = (executable.parent / "activate")
                    tmp_file = tempfile.NamedTemporaryFile("w", delete=False)
                    tmp_file_content = []
                    if venv.exists():
                        tmp_file_content.append(f"source {str(venv)}")
                    tmp_file_content.append(f"""{self.command} {" ".join(f'"{a}"' for a in self.arguments)}""")
                    tmp_file.write("\n".join(tmp_file_content))
                    LOGGER.debug("Running:" + ";".join(tmp_file_content))
                    tmp_file.close()
                    r = subprocess.run(f"/bin/bash {tmp_file.name}",
                                       shell=True,
                                       env=_e,
                                       check=True)
                    os.remove(tmp_file.name)
                    if r.returncode != 0:
                        LOGGER.error(f"Error during step [green bold]{self.id}[/]")
                        self.status = "RunError"
                    else:
                        LOGGER.info(f"Done running step [green bold]{self.id}[/]")
                        self.status = "Done"
                except subprocess.CalledProcessError:
                    LOGGER.error(f"Error during step [green bold]{self.id}[/]")
                    self.status = "RunError"
        return self.status

    def check_env(self):
        r = dict()
        if not self.skipped:
            for k, v in self.environment.items():
                if v.effective_value() is None and v.is_required():
                    r[k] = v.description
        return r

    def simple_repr(self):
        if self.description:
            return f"{self.id} ({self.status}): {self.description}"
        return f"{self.id} ({self.status})"

    def __str__(self):
        r = list()
        r.append(f"Step {self.id}")
        r.append(f"Command: {self.command}" + ("" if not self.arguments else " " + " ".join(self.arguments)))
        if self.description:
            r.append("Description:")
            r.append(f"  {self.description}")
        if self.environment:
            r.append("Environment:")
            for k, v in self.environment.items():
                optional_str = "" if not v.optional else "(Optional)"
                if v.description:
                    r.append(f"- {k}{optional_str}: {v.description}")
                else:
                    r.append(f"- {k}{optional_str}")
        if self.useSystemEnvironment:
            r.append("[yellow]Use system environment variables[/]")
        if self.skipped:
            r.append("[red]Skipped by user[/]")
        r.append(f"Status: {self.status}")
        return "\n".join(r)

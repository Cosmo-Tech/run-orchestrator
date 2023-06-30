import json
import os
import pathlib
import subprocess
import sys
from dataclasses import dataclass
from dataclasses import field
from typing import Union

import flowpipe
import jsonschema

from cosmotech.orchestrator.utils.logger import LOGGER


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


@dataclass
class EnvironmentVariable:
    name: str = field()
    defaultValue: str = field(default=None)
    value: str = field(default=None)
    description: str = field(default=None)

    def is_required(self):
        return not self.value and not self.defaultValue

    def effective_value(self):
        v = self.value or os.environ.get(self.name, self.defaultValue)
        if v is not None:
            return str(v)
        return None

    def join(self, other: 'EnvironmentVariable'):
        self.defaultValue = self.defaultValue or other.defaultValue
        self.value = self.value or other.value
        self.description = self.description or other.description


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


@dataclass
class Step:
    id: str = field()
    commandId: str = field(default=None)
    command: str = field(default=None)
    arguments: list[str] = field(default_factory=list)
    environment: dict[str, Union[EnvironmentVariable, dict]] = field(default_factory=dict)
    precedents: list[Union[str, 'Step']] = field(default_factory=list)
    loaded = False
    status = None

    def load_command(self, available_commands):
        if not self.commandId or self.loaded:
            LOGGER.debug(f"[green bold]{self.id}[/] already ready")
            return
        if self.commandId not in available_commands:
            self.status = "Error"
            LOGGER.error(f"[green bold]{self.id}[/] asks for a non existing template [cyan bold]{self.commandId}[/]")
            raise ValueError(f"Command Template {self.commandId} is not available")
        command = available_commands[self.commandId]
        LOGGER.debug(f"[green bold]{self.id}[/] loads template [cyan bold]{self.commandId}[/]")
        self.command = command.command
        self.arguments = command.arguments[:] + self.arguments
        for _env_key, _env in command.environment.items():
            if _env_key in self.environment:
                self.environment[_env_key].join(_env)
            else:
                self.environment[_env_key] = _env

    def link_precedents(self, available_steps, node):
        _precedents = []
        LOGGER.debug(f"Looking previous steps for [green bold]{self.id}[/]")
        for _p in self.precedents:
            if isinstance(_p, str):
                if _p not in available_steps:
                    self.status = "Error"
                    raise ValueError(f"Step {_p} does not exists")
                s, n = available_steps.get(_p)
                _precedents.append(s)
                n.outputs['status'].connect(node.inputs['previous'][_p])
                LOGGER.debug(f" - Found [green bold]{_p}[/]")
        self.precedents = _precedents

    def __post_init__(self):
        if not bool(self.command) ^ bool(self.commandId):
            self.status = "Error"
            raise ValueError("A step requires either a command or a commandId")
        if self.command:
            self.loaded = True
        tmp_env = dict()
        for k, v in self.environment.items():
            tmp_env[k] = EnvironmentVariable(k, **v)
        self.environment = tmp_env
        self.status = "Init"

    def _effective_env(self):
        _env = dict()
        for k, v in self.environment.items():
            _v = v.effective_value()
            if _v is None:
                _v = ""
            _env[k] = _v
        return _env

    def run(self, dry: bool = False):
        @flowpipe.Node(outputs=["status"])
        def f(previous):
            LOGGER.info(f"Starting step [green bold]{self.id}[/]")
            self.status = "Ready"
            if isinstance(previous, dict) and any(map(lambda a: a not in ['Done', 'DryRun'], previous.values())):
                LOGGER.warning(f"Skipping step [green bold]{self.id}[/] due to previous errors")
                self.status = "Skipped"
            if self.status == "Ready":
                if dry:
                    self.status = "DryRun"
                else:
                    _e = self._effective_env()
                    try:
                        executable = pathlib.Path(sys.executable)
                        venv = (executable.parent / "activate")
                        cmd_line = list()
                        cmd_line.append("bash -c")
                        sub_command = list()
                        if venv.exists():
                            sub_command.append(f"source {str(venv)};")
                        sub_command.append(self.command)
                        sub_command.extend(self.arguments)
                        cmd_line.append("\"" + " ".join(sub_command) + "\"")
                        LOGGER.info(" ".join(cmd_line))
                        r = subprocess.run(" ".join(cmd_line),
                                           shell=True,
                                           env=_e,
                                           check=True)
                        self.status = "Done"
                        LOGGER.info(f"Done running step [green bold]{self.id}[/]")
                    except subprocess.CalledProcessError:
                        LOGGER.error(f"Error during step [green bold]{self.id}[/]")
                        self.status = "RunError"
            return {'status': self.status}

        return f

    def check_env(self):
        r = dict()
        for k, v in self.environment.items():
            if v.effective_value() is None:
                r[k] = v.description
        return r

    def __repr__(self):
        r = list()
        r.append(f"Step {self.id}")
        r.append(f"Command: {self.command}" + ("" if not self.arguments else " " + " ".join(self.arguments)))
        if self.environment:
            r.append("Environment:")
            for k, v in self.environment.items():
                if v.description:
                    r.append(f"- {k}: {v.description}")
                else:
                    r.append(f"- {k}")
        r.append(f"Status: {self.status}")
        return "\n".join(r)


class Orchestrator(metaclass=Singleton):

    @staticmethod
    def __load_item(container, object_type, override, type_msg, **item):
        id = item.get('id')
        if id in container and not override:
            raise ValueError(f"{type_msg} {id} is already defined")
        _item = object_type(**item)
        container[id] = _item
        return _item

    def load_command(self, container, override: bool = False, **command) -> CommandTemplate:
        return self.__load_item(container=container,
                                object_type=CommandTemplate,
                                override=override,
                                type_msg="Command Template",
                                **command)

    def load_step(self, container, override: bool = False, **step) -> Step:
        return self.__load_item(container=container,
                                object_type=Step,
                                override=override,
                                type_msg="Step",
                                **step)

    def load_json_file(self, json_file_path, dry: bool = False, display_env: bool = False):
        _path = pathlib.Path(json_file_path)
        g = flowpipe.Graph(name=json_file_path)
        steps: dict[str, (Step, flowpipe.Node)] = dict()
        commands: dict[str, CommandTemplate] = dict()
        l = json.load(open(_path))
        schema_path = pathlib.Path(__file__).parent / "schema/run_template_json_schema.json"
        schema = json.load(open(schema_path))
        jsonschema.validate(l, schema)
        for tmpl in l.get("commandTemplates", list()):
            self.load_command(commands, **tmpl)
        for step in l.get("steps", list()):
            id = step.get('id')
            s = self.load_step(steps, **step)
            node = s.run(dry)(graph=g, name=id)
            steps[id] = (s, node)
            s.load_command(commands)
        missing_env = dict()
        for s, n in steps.values():
            s.link_precedents(steps, node=n)
            missing_env.update(s.check_env())
        if display_env:
            _env: dict[str, set] = dict()
            for s, n in steps.values():
                for k, v in s.environment.items():
                    _env.setdefault(k, set())
                    if v.description:
                        _env[k].add(v.description)
            LOGGER.info(f"Environment variable defined for {_path.name}")
            for k, v in sorted(_env.items(), key=lambda a: a[0]):
                desc = (":\n  - " + "\n  - ".join(v)) if len(v) > 1 else (": " + list(v)[0] if len(v) else "")
                LOGGER.info(f" - [yellow]{k}[/]{desc}")
        elif missing_env:
            LOGGER.error("Missing environment values")
            for k, v in missing_env.items():
                LOGGER.error(f" - {k}" + (f": {v}" if v else ""))
            raise ValueError("Missing environment variables, check the logs")
        return commands, steps, g

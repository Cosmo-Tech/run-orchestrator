# Copyright (C) - 2023 - 2023 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import json
import pathlib

import flowpipe
import jsonschema

from cosmotech.orchestrator.core.command_template import CommandTemplate
from cosmotech.orchestrator.core.runner import Runner
from cosmotech.orchestrator.core.step import Step
from cosmotech.orchestrator.templates.library import Library
from cosmotech.orchestrator.templates.plugin import Plugin
from cosmotech.orchestrator.utils.logger import LOGGER
from cosmotech.orchestrator.utils.singleton import Singleton


class Orchestrator(metaclass=Singleton):

    def __init__(self):
        self.library = Library()

    @staticmethod
    def load_step(container, override: bool = False, **step) -> Step:
        _id = step.get('id')
        LOGGER.debug(f"Loading [green bold]{_id}[/] of type [yellow bold]Step[/]")
        if _id in container and not override:
            raise ValueError(f"Step {_id} is already defined")
        _item = Step(**step)
        container[_id] = _item
        return _item

    def load_json_file(
        self, json_file_path,
        dry: bool = False,
        display_env: bool = False,
        skipped_steps: list[str] = (),
        validate_only: bool = False,
        ignore_error: bool = False
    ):
        _path = pathlib.Path(json_file_path)
        _run_content = json.load(open(_path))
        schema_path = pathlib.Path(__file__).parent.parent / "schema/run_template_json_schema.json"
        schema = json.load(open(schema_path))
        jsonschema.validate(_run_content, schema)
        if validate_only:
            LOGGER.info(f"[green bold]{_path}[/] is a valid orchestration file")
            return None, None, None
        return self._load_from_json_content(json_file_path, _run_content, dry, display_env, skipped_steps, ignore_error)

    def _load_from_json_content(
        self, json_file_path, _run_content,
        dry: bool = False,
        display_env: bool = False,
        skipped_steps: list[str] = (),
        ignore_error: bool = False
    ):
        g = flowpipe.Graph(name=json_file_path)
        steps: dict[str, (Step, flowpipe.Node)] = dict()
        commands: dict[str, CommandTemplate] = dict()
        plugin = Plugin(json_file_path)
        plugin.name = json_file_path
        for tmpl in _run_content.get("commandTemplates", list()):
            _template = plugin.register_template(tmpl)
            if _template:
                commands[_template.id] = _template
        self.library.load_plugin(plugin)
        self.library.display_library(log_function=LOGGER.debug, verbose=False)
        for step in _run_content.get("steps", list()):
            _id = step.get('id')
            s = self.load_step(steps, **step)
            if _id in skipped_steps:
                s.skipped = True
            node = Runner(graph=g, name=_id, step=s, dry_run=dry)
            steps[_id] = (s, node)
        missing_env = dict()
        for _step, _node in steps.values():
            if _step.precedents:
                LOGGER.debug(f"Dependencies of [green bold]{_step.id}[/]:")
            else:
                LOGGER.debug(f"No dependencies for [green bold]{_step.id}[/]")
            for _precedent in _step.precedents:
                if isinstance(_precedent, str):
                    if _precedent not in steps:
                        _step.status = "Error"
                        raise ValueError(f"Step {_precedent} does not exists")
                    _prec_step, _prec_node = steps.get(_precedent)
                    _prec_node.outputs['status'].connect(_node.inputs['previous'][_precedent])
                    LOGGER.debug(f" - Found [green bold]{_precedent}[/]")
            missing_env.update(_step.check_env())
        if display_env:
            _env: dict[str, set] = dict()
            for s, n in steps.values():
                for k, v in s.environment.items():
                    _env.setdefault(k, set())
                    if v.description:
                        _env[k].add(v.description)
            _path = pathlib.Path(json_file_path)
            LOGGER.info(f"Environment variable defined for {_path.name}")
            for k, v in sorted(_env.items(), key=lambda a: a[0]):
                desc = (":\n  - " + "\n  - ".join(v)) if len(v) > 1 else (": " + list(v)[0] if len(v) else "")
                LOGGER.info(f" - [yellow]{k}[/]{desc}")
        elif missing_env and not ignore_error:
            LOGGER.error("Missing environment values")
            for k, v in missing_env.items():
                LOGGER.error(f" - {k}" + (f": {v}" if v else ""))
            raise ValueError("Missing environment variables, check the logs")
        return commands, steps, g

# Copyright (C) - 2023 - 2025 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import json
import pathlib

import flowpipe
import jsonschema

from cosmotech.orchestrator.core.runner import Runner
from cosmotech.orchestrator.core.step import Step
from cosmotech.orchestrator.core.step import StepStatus
from cosmotech.orchestrator.templates.library import Library
from cosmotech.orchestrator.templates.plugin import Plugin
from cosmotech.orchestrator.utils.logger import LOGGER
from cosmotech.orchestrator.utils.singleton import Singleton
from cosmotech.orchestrator.utils.translate import T


class FileLoader:
    @staticmethod
    def load_step(container, override: bool = False, **step) -> Step:
        _id = step.get("id")
        LOGGER.debug(T("csm-orc.orchestrator.core.orchestrator.loading_step").format(id=f"{_id} of type Step"))
        if _id in container and not override:
            raise ValueError(T("csm-orc.orchestrator.core.orchestrator.step_already_defined").format(step_id=_id))
        _item = Step(**step)
        container[_id] = _item
        return _item

    def __init__(self, file_path):
        self.file_path = file_path
        self.library = Library()

    def __call__(self, skipped_steps: list[str] = ()):
        _path = pathlib.Path(self.file_path)
        _run_content = json.load(_path.open())
        schema_path = pathlib.Path(__file__).parent.parent / "schema/run_template_json_schema.json"
        schema = json.load(schema_path.open())
        jsonschema.validate(_run_content, schema)
        steps: dict[str, Step] = dict()
        plugin = Plugin(self.file_path)
        plugin.name = self.file_path
        for tmpl in _run_content.get("commandTemplates", list()):
            _template = plugin.register_template(tmpl)
        self.library.load_plugin(plugin)
        for step in _run_content.get("steps", list()):
            _id = step.get("id")
            s = self.load_step(steps, **step)
            if _id in skipped_steps:
                s.skipped = True
            steps[_id] = s

        return steps


class Orchestrator(metaclass=Singleton):
    def __init__(self):
        self.library = Library()

    def load_json_file(
        self,
        json_file_path,
        dry: bool = False,
        display_env: bool = False,
        skipped_steps: list[str] = (),
        validate_only: bool = False,
        ignore_error: bool = False,
    ):
        # Call a loader class for the orchestration file to get steps
        steps = FileLoader(json_file_path)(skipped_steps=skipped_steps)
        Library().display_library(log_function=LOGGER.debug, verbose=False)
        if validate_only:
            LOGGER.info(T("csm-orc.orchestrator.core.orchestrator.valid_file").format(file_path=json_file_path))
            return None, None
        return self._load_from_json_content(json_file_path, steps, dry, display_env, ignore_error)

    @staticmethod
    def _load_from_json_content(
        json_file_path, steps: dict[str, Step], dry: bool = False, display_env: bool = False, ignore_error: bool = False
    ):
        _graph = flowpipe.Graph(name=json_file_path)
        _steps: dict[str, (Step, flowpipe.Node)] = dict()

        # Generate flowpipe runners for execution
        for k, v in steps.items():
            node = Runner(graph=_graph, name=k, step=v, dry_run=dry)
            _steps[k] = (v, node)

        # Check for missing environment variable and instantiate DAG
        missing_env = dict()
        for _step, _node in _steps.values():
            if _step.precedents:
                LOGGER.debug(T("csm-orc.orchestrator.core.orchestrator.dependencies.header").format(step_id=_step.id))
            else:
                LOGGER.debug(
                    T("csm-orc.orchestrator.core.orchestrator.dependencies.no_dependencies").format(step_id=_step.id)
                )
            for _precedent in _step.precedents:
                if isinstance(_precedent, str):
                    if _precedent not in _steps:
                        _step.status = StepStatus.ERROR
                        raise ValueError(
                            T("csm-orc.orchestrator.core.orchestrator.step_not_exists").format(step_id=_precedent)
                        )
                    _prec_step, _prec_node = _steps.get(_precedent)
                    _prec_node.outputs["status"].connect(_node.inputs["previous"][_precedent])
                    LOGGER.debug(
                        T("csm-orc.orchestrator.core.orchestrator.dependencies.found").format(precedent=_precedent)
                    )

                    # Connect data flows based on input configuration
                    for input_name, input_config in _step.inputs.items():
                        if input_config["stepId"] == _precedent:
                            # Check if either input or output is hidden
                            is_hidden = input_config.get("hidden", False) or (
                                input_config["stepId"] in steps
                                and input_config["output"] in steps[input_config["stepId"]].outputs
                                and steps[input_config["stepId"]].outputs[input_config["output"]].get("hidden", False)
                            )

                            if is_hidden:
                                LOGGER.debug(
                                    T("csm-orc.orchestrator.core.orchestrator.data_flow.connecting_hidden").format(
                                        from_step=input_config["stepId"],
                                        from_output=input_config["output"],
                                        to_step=_step.id,
                                        to_input=input_name,
                                    )
                                )
                            else:
                                LOGGER.debug(
                                    T("csm-orc.orchestrator.core.orchestrator.data_flow.connecting").format(
                                        from_step=input_config["stepId"],
                                        from_output=input_config["output"],
                                        to_step=_step.id,
                                        to_input=input_name,
                                    )
                                )
                            # Connect the output_data to input_data
                            _prec_node.outputs["output_data"].connect(_node.inputs["input_data"])
            if _step_missing_env := _step.check_env():
                missing_env[_step.id] = _step_missing_env
        if display_env:
            # Pure display of environment variables names and descriptions
            _env: dict[str, set] = dict()
            for s, n in _steps.values():
                for k, v in s.environment.items():
                    _env.setdefault(k, set())
                    if v.description:
                        _env[k].add(v.description)
            _path = pathlib.Path(json_file_path)
            LOGGER.info(T("csm-orc.orchestrator.core.orchestrator.environment.defined").format(file_name=_path.name))
            for k, v in sorted(_env.items(), key=lambda a: a[0]):
                desc = (":\n    - " + "\n    - ".join(v)) if len(v) > 1 else (": " + list(v)[0] if len(v) else "")
                LOGGER.info(
                    T("csm-orc.orchestrator.core.orchestrator.environment.variable").format(key=k, description=desc)
                )
        elif missing_env and not ignore_error:
            for _step_id, variables in missing_env.items():
                LOGGER.error(T("csm-orc.orchestrator.core.orchestrator.environment.missing").format(step_id=_step_id))
                for k, v in variables.items():
                    LOGGER.error(
                        T("csm-orc.orchestrator.core.orchestrator.environment.missing_value").format(
                            key=k, value=v if v else ""
                        )
                    )
            raise ValueError(T("csm-orc.orchestrator.errors.missing_env_vars"))
        return _steps, _graph

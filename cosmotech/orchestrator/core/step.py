# Copyright (C) - 2023 - 2025 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.
import logging
import os
import pathlib
import queue
import subprocess
import tempfile
import threading
from dataclasses import InitVar
from dataclasses import dataclass
from dataclasses import field
from typing import TextIO
from typing import Union

import sys

from cosmotech.orchestrator.core.command_template import CommandTemplate
from cosmotech.orchestrator.core.environment import EnvironmentVariable
from cosmotech.orchestrator.templates.library import Library
from cosmotech.orchestrator.utils.logger import LOGGER
from cosmotech.orchestrator.utils.translate import T


from enum import Enum


class StepStatus(Enum):
    CREATED = 0
    INITIALIZED = 1
    SUCCESS = 2
    SKIPPED_BY_USER = 3
    SKIPPED_AFTER_FAILURE = 4
    ERROR = 5
    DRY_RUN = 6


@dataclass
class Step:
    id: str = field()
    commandId: str = field(default=None)
    command: str = field(default=None)
    description: str = field(default=None)
    arguments: list[str] = field(default_factory=list)
    environment: dict[str, Union[EnvironmentVariable, dict]] = field(default_factory=dict)
    precedents: list[Union[str, "Step"]] = field(default_factory=list)
    useSystemEnvironment: bool = field(default=True)
    outputs: dict = field(default_factory=dict)
    inputs: dict = field(default_factory=dict)
    captured_output: dict = field(default_factory=dict)
    loaded = False
    status: StepStatus = StepStatus.CREATED
    skipped = False
    stop_library_load: InitVar[bool] = field(default=False, repr=False)

    class OutputParser(threading.Thread):
        def __init__(self, stream: TextIO, output_queue: queue.Queue, is_stderr: bool = False):
            super().__init__()
            self.stream = stream
            self.queue = output_queue
            self.is_stderr = is_stderr
            self.outputs = {}
            self.daemon = True  # Thread will exit when main program exits

        def run(self):
            for line in iter(self.stream.readline, ""):
                line = line.rstrip("\n")
                if line.startswith("CSM-OUTPUT-DATA:") and not self.is_stderr:
                    try:
                        _, output_name, value = line.split(":", 2)
                        self.outputs[output_name] = value.strip()
                    except ValueError:
                        pass
                else:
                    # Queue tuple of (is_stderr, line) for logging
                    self.queue.put((self.is_stderr, line))
            self.stream.close()

    def _process_output_queue(self, output_queue: queue.Queue, process: subprocess.Popen) -> None:
        """Process output queue until subprocess completes"""
        while True:
            # Check if process has completed
            if process.poll() is not None and output_queue.empty():
                break

            try:
                # Get output with timeout to allow checking process status
                is_stderr, line = output_queue.get(timeout=0.1)
                if is_stderr:
                    self.processed_output_logger.error(line)
                else:
                    self.processed_output_logger.info(line)
                output_queue.task_done()
            except queue.Empty:
                continue

    def __load_command_from_library(self):
        library = Library()
        if not self.commandId or self.loaded:
            LOGGER.debug(T("csm-orc.orchestrator.core.step.already_ready").format(step_id=self.display_id))
            return

        self.display_command_id = self.commandId
        command: CommandTemplate = library.find_template_by_name(self.commandId)
        if command is None:
            self.StepStatus = StepStatus.ERROR
            LOGGER.error(
                T("csm-orc.orchestrator.core.step.template_not_found").format(
                    step_id=self.display_id, command_id=self.display_command_id
                )
            )
            raise ValueError(T("csm-orc.orchestrator.core.step.template_unavailable").format(command_id=self.commandId))
        LOGGER.debug(
            T("csm-orc.orchestrator.core.step.loading_template").format(
                step_id=self.display_id, command_id=self.display_command_id
            )
        )
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

    def __post_init__(self, stop_library_load):
        if not bool(self.command) ^ bool(self.commandId):
            self.status = StepStatus.ERROR
            raise ValueError(T("csm-orc.orchestrator.core.step.command_required"))
        tmp_env = dict()
        for k, v in self.environment.items():
            tmp_env[k] = EnvironmentVariable(k, **v)
        self.environment = tmp_env
        self.status = StepStatus.INITIALIZED
        self.display_id = self.id
        if self.commandId and not stop_library_load:
            self.__load_command_from_library()
            self.commandId = None
        self.loaded = True
        self.processed_output_logger = logging.getLogger("csm-orc.run.step.output_parser")
        if not self.processed_output_logger.hasHandlers():
            __handler = logging.StreamHandler(sys.stdout)
            __handler.setFormatter(logging.Formatter("{message}", style="{"))
            self.processed_output_logger.addHandler(__handler)
            self.processed_output_logger.setLevel(logging.INFO)

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
                    continue
                _v = ""
            _env[k] = _v
        # Special case for some standard env var (mostly the ones configured in the docker image by default)
        # This avoids needing to add "useSystemEnvironment" in every/most steps
        for env_name in ["PATH", "PYTHONPATH", "LD_LIBRARY_PATH", "SSL_CERT_DIR"]:
            if env_name not in _env and os.environ.get(env_name):
                _env[env_name] = os.environ.get(env_name)
        return _env

    def run(self, dry: bool = False, previous=None, input_data: dict = None, as_exit: bool = False):
        if previous is None:
            previous = dict()
        if input_data is None:
            input_data = {}

        step_type = "step"
        if as_exit:
            step_type = "exit handler"

        LOGGER.info(T("csm-orc.orchestrator.core.step.starting").format(step_type=step_type, step_id=self.display_id))

        if isinstance(previous, dict) and any(
            map(
                lambda a: a not in [StepStatus.SUCCESS, StepStatus.DRY_RUN, StepStatus.SKIPPED_BY_USER],
                previous.values(),
            )
        ):
            LOGGER.warning(
                T("csm-orc.orchestrator.core.step.skipping_previous_errors").format(
                    step_type=step_type, step_id=self.display_id
                )
            )
            self.status = StepStatus.SKIPPED_AFTER_FAILURE

        if self.status == StepStatus.INITIALIZED:
            if self.skipped:
                LOGGER.info(
                    T("csm-orc.orchestrator.core.step.skipping_as_required").format(
                        step_type=step_type, step_id=self.display_id
                    )
                )
                self.status = StepStatus.SKIPPED_BY_USER
            elif dry:
                self.status = StepStatus.DRY_RUN
            else:
                # Set up environment with input data
                _e = self._effective_env()
                for input_name, input_config in self.inputs.items():
                    value = input_data.get(input_name)
                    if value is None and "defaultValue" in input_config:
                        value = input_config["defaultValue"]
                        if input_config.get("hidden", False):
                            LOGGER.debug(
                                T("csm-orc.orchestrator.core.step.input.default_value_hidden").format(
                                    step_id=self.id, input=input_name
                                )
                            )
                        else:
                            LOGGER.debug(
                                T("csm-orc.orchestrator.core.step.input.default_value").format(
                                    step_id=self.id, input=input_name, value=value
                                )
                            )

                    if value is not None:
                        _e[input_config["as"]] = value
                    elif not input_config.get("optional", False):
                        raise ValueError(
                            T("csm-orc.orchestrator.core.step.input.missing_required").format(
                                step_id=self.id, input=input_name
                            )
                        )

                if self.useSystemEnvironment:
                    _e = {**os.environ, **_e}

                try:
                    executable = pathlib.Path(sys.executable)
                    venv = executable.parent / "activate"
                    tmp_file = tempfile.NamedTemporaryFile("w", delete=False)
                    tmp_file_content = []
                    if venv.exists():
                        tmp_file_content.append(f"source {str(venv)}")
                    tmp_file_content.append(f"""{self.command} {" ".join(f'"{a}"' for a in self.arguments)}""")
                    tmp_file.write("\n".join(tmp_file_content))
                    LOGGER.debug(
                        T("csm-orc.orchestrator.core.step.running_command").format(command=";".join(tmp_file_content))
                    )
                    tmp_file.close()

                    # Start process with pipes
                    process = subprocess.Popen(
                        f"/bin/bash {tmp_file.name}",
                        shell=True,
                        env=_e,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        bufsize=1,  # Line buffered
                        universal_newlines=True,
                    )

                    # Create queue for output processing
                    output_queue = queue.Queue()

                    # Start output parser threads
                    stdout_parser = self.OutputParser(process.stdout, output_queue, is_stderr=False)
                    stderr_parser = self.OutputParser(process.stderr, output_queue, is_stderr=True)

                    stdout_parser.start()
                    stderr_parser.start()

                    # Process output queue until completion
                    self._process_output_queue(output_queue, process)

                    # Wait for parser threads to complete
                    stdout_parser.join()
                    stderr_parser.join()

                    # Clean up temporary file
                    os.remove(tmp_file.name)

                    # Get return code
                    return_code = process.wait()

                    if return_code != 0:
                        raise subprocess.CalledProcessError(return_code, self.command)

                    # Get captured outputs
                    self.captured_output = {}

                    # First set defaults
                    for output_name, output_config in self.outputs.items():
                        if "defaultValue" in output_config:
                            self.captured_output[output_name] = output_config["defaultValue"]
                            if output_config.get("hidden", False):
                                LOGGER.debug(
                                    T("csm-orc.orchestrator.core.step.output.default_value_hidden").format(
                                        step_id=self.id, output=output_name
                                    )
                                )
                            else:
                                LOGGER.debug(
                                    T("csm-orc.orchestrator.core.step.output.default_value").format(
                                        step_id=self.id, output=output_name, value=output_config["defaultValue"]
                                    )
                                )

                    # Then override with actual outputs
                    self.captured_output.update(stdout_parser.outputs)

                    # Log all final output values
                    LOGGER.debug(
                        T("csm-orc.orchestrator.core.step.output.captured_values_header").format(step_id=self.id)
                    )
                    for output_name, value in self.captured_output.items():
                        if output_name in self.outputs and self.outputs[output_name].get("hidden", False):
                            LOGGER.debug(
                                T("csm-orc.orchestrator.core.step.output.captured_hidden").format(output=output_name)
                            )
                        else:
                            LOGGER.debug(
                                T("csm-orc.orchestrator.core.step.output.captured_value").format(
                                    output=output_name, value=value
                                )
                            )

                    # Validate required outputs
                    missing_outputs = []
                    for output_name, output_config in self.outputs.items():
                        if (
                            output_name not in self.captured_output
                            and not output_config.get("optional", False)
                            and "defaultValue" not in output_config
                        ):
                            missing_outputs.append(output_name)
                            LOGGER.debug(
                                T("csm-orc.orchestrator.core.step.output.missing_value").format(
                                    step_id=self.id, output=output_name
                                )
                            )

                    if missing_outputs:
                        raise ValueError(
                            T("csm-orc.orchestrator.core.step.output.missing_required").format(
                                step_id=self.id, outputs=", ".join(missing_outputs)
                            )
                        )

                    LOGGER.info(
                        T("csm-orc.orchestrator.core.step.done_running").format(
                            step_type=step_type, step_id=self.display_id
                        )
                    )
                    self.status = StepStatus.SUCCESS

                except subprocess.CalledProcessError as e:
                    LOGGER.error(
                        T("csm-orc.orchestrator.core.step.error_during").format(
                            step_type=step_type, step_id=self.display_id
                        )
                    )
                    LOGGER.error(str(e))
                    self.status = StepStatus.ERROR

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
            return T("csm-orc.orchestrator.core.step.info.simple_repr").format(
                id=self.id, status=self.status.name, description=self.description
            )
        return T("csm-orc.orchestrator.core.step.info.simple_repr_no_desc").format(id=self.id, status=self.status.name)

    def __str__(self):
        r = list()
        r.append(T("csm-orc.orchestrator.core.step.info.header").format(id=self.id))
        r.append(
            T("csm-orc.orchestrator.core.step.info.command").format(
                command=self.command + ("" if not self.arguments else " " + " ".join(self.arguments))
            )
        )
        if self.description:
            r.append(T("csm-orc.orchestrator.core.step.info.description_header"))
            r.append(f"  {self.description}")
        if self.environment:
            r.append(T("csm-orc.orchestrator.core.step.info.environment_header"))
            for k, v in self.environment.items():
                optional_str = "" if not v.optional else T("csm-orc.orchestrator.core.step.info.optional")
                if v.description:
                    r.append(f"- {k} {optional_str}: {v.description}")
                else:
                    r.append(f"- {k} {optional_str}")
        if self.useSystemEnvironment:
            r.append(T("csm-orc.orchestrator.core.step.info.use_system_env"))
        if self.skipped:
            r.append(T("csm-orc.orchestrator.core.step.info.skipped"))
        r.append(T("csm-orc.orchestrator.core.step.info.status").format(status=self.status.name))
        return "\n".join(r)

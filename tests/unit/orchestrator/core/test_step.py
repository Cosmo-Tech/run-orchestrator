import pytest
from unittest.mock import MagicMock, patch, mock_open, call
import os
import subprocess
import tempfile
import threading
import queue
import sys
from pathlib import Path

from cosmotech.orchestrator.core.step import Step, StepStatus
from cosmotech.orchestrator.core.environment import EnvironmentVariable
from cosmotech.orchestrator.templates.library import Library


class TestStep:
    def test_post_init_converts_environment_dict_to_env_vars(self):
        # Setup
        env_dict = {
            "TEST_VAR1": {"value": "value1", "description": "Test var 1"},
            "TEST_VAR2": {"defaultValue": "default2", "description": "Test var 2"},
        }

        # Execute
        step = Step(id="test-step", command="echo", environment=env_dict)

        # Verify
        assert isinstance(step.environment["TEST_VAR1"], EnvironmentVariable)
        assert isinstance(step.environment["TEST_VAR2"], EnvironmentVariable)
        assert step.environment["TEST_VAR1"].name == "TEST_VAR1"
        assert step.environment["TEST_VAR1"].value == "value1"
        assert step.environment["TEST_VAR1"].description == "Test var 1"
        assert step.environment["TEST_VAR2"].name == "TEST_VAR2"
        assert step.environment["TEST_VAR2"].defaultValue == "default2"
        assert step.environment["TEST_VAR2"].description == "Test var 2"

    def test_post_init_requires_command_or_command_id(self):
        # Execute and verify
        with pytest.raises(ValueError):
            Step(id="test-step")

        with pytest.raises(ValueError):
            Step(id="test-step", command="echo", commandId="echo")

        # These should not raise errors
        Step(id="test-step", command="echo")
        Step(id="test-step", commandId="echo", stop_library_load=True)

    @patch("cosmotech.orchestrator.core.step.Library")
    def test_load_command_from_library(self, mock_library_class):
        # Setup
        mock_library = MagicMock()
        mock_library_class.return_value = mock_library

        template = MagicMock()
        template.command = "echo"
        template.arguments = ["Hello", "World"]
        template.environment = {"TEST_VAR": EnvironmentVariable(name="TEST_VAR", value="test_value")}
        template.description = "Test template"
        template.useSystemEnvironment = True

        mock_library.find_template_by_name.return_value = template

        # Execute
        step = Step(id="test-step", commandId="test-template")

        # Verify
        mock_library.find_template_by_name.assert_called_once_with("test-template")
        assert step.command == "echo"
        assert step.arguments == ["Hello", "World"]
        assert "TEST_VAR" in step.environment
        assert step.description == "Test template"
        assert step.useSystemEnvironment is True

    @patch("cosmotech.orchestrator.core.step.Library")
    def test_load_command_from_library_not_found(self, mock_library_class):
        # Setup
        mock_library = MagicMock()
        mock_library_class.return_value = mock_library
        mock_library.find_template_by_name.return_value = None

        # Execute and verify
        with pytest.raises(ValueError):
            Step(id="test-step", commandId="non-existent-template")

    @patch("cosmotech.orchestrator.core.step.Library")
    def test_load_command_from_library_with_environment_merge(self, mock_library_class):
        # Setup
        mock_library = MagicMock()
        mock_library_class.return_value = mock_library

        template = MagicMock()
        template.command = "echo"
        template.arguments = []
        template.environment = {
            "TEMPLATE_VAR": EnvironmentVariable(name="TEMPLATE_VAR", value="template_value"),
            "COMMON_VAR": EnvironmentVariable(name="COMMON_VAR", defaultValue="template_default"),
        }
        template.description = None
        template.useSystemEnvironment = False

        mock_library.find_template_by_name.return_value = template

        # Execute
        step = Step(
            id="test-step",
            commandId="test-template",
            environment={"STEP_VAR": {"value": "step_value"}, "COMMON_VAR": {"value": "step_value"}},
            description="Step description",
        )

        # Verify
        assert "TEMPLATE_VAR" in step.environment
        assert "STEP_VAR" in step.environment
        assert "COMMON_VAR" in step.environment
        assert step.environment["COMMON_VAR"].value == "step_value"
        assert step.description == "Step description"

    def test_serialize(self):
        # Setup
        step = Step(
            id="test-step",
            command="echo",
            arguments=["Hello", "World"],
            environment={"TEST_VAR": {"value": "test_value"}},
            precedents=["step1", "step2"],
            description="Test step",
            useSystemEnvironment=True,
        )

        # Execute
        result = step.serialize()

        # Verify
        assert result["id"] == "test-step"
        assert result["command"] == "echo"
        assert result["arguments"] == ["Hello", "World"]
        assert "environment" in result
        assert "precedents" in result
        assert result["description"] == "Test step"
        assert result["useSystemEnvironment"] is True

    def test_effective_env(self):
        # Setup
        env_var1 = MagicMock()
        env_var1.effective_value.return_value = "value1"
        env_var1.optional = False

        env_var2 = MagicMock()
        env_var2.effective_value.return_value = None
        env_var2.optional = True

        env_var3 = MagicMock()
        env_var3.effective_value.return_value = None
        env_var3.optional = False

        step = Step(id="test-step", command="echo")
        step.environment = {"ENV_VAR1": env_var1, "ENV_VAR2": env_var2, "ENV_VAR3": env_var3}

        # Execute
        result = step._effective_env()

        # Verify
        assert "ENV_VAR1" in result
        assert result["ENV_VAR1"] == "value1"
        assert "ENV_VAR2" not in result
        assert "ENV_VAR3" in result
        assert result["ENV_VAR3"] == ""

    @patch.dict(os.environ, {"PATH": "/usr/bin", "PYTHONPATH": "/usr/lib/python"})
    def test_effective_env_includes_standard_env_vars(self):
        # Setup
        step = Step(id="test-step", command="echo")

        # Execute
        result = step._effective_env()

        # Verify
        assert "PATH" in result
        assert result["PATH"] == "/usr/bin"
        assert "PYTHONPATH" in result
        assert result["PYTHONPATH"] == "/usr/lib/python"

    @patch("tempfile.NamedTemporaryFile")
    @patch("subprocess.Popen")
    @patch("os.remove")
    def test_run_successful_command(self, mock_remove, mock_popen, mock_temp_file):
        # Setup
        mock_file = MagicMock()
        mock_temp_file.return_value = mock_file
        mock_file.name = "/tmp/test_file"

        mock_process = MagicMock()
        mock_process.stdout.readline.side_effect = ["Output line 1\n", "CSM-OUTPUT-DATA:output1:value1\n", ""]
        mock_process.stderr.readline.side_effect = [""]
        mock_process.poll.side_effect = [None, None, 0]
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process

        step = Step(id="test-step", command="echo", arguments=["Hello", "World"])

        # Execute
        result = step.run()

        # Verify
        assert result == StepStatus.SUCCESS
        assert step.status == StepStatus.SUCCESS
        assert "output1" in step.captured_output
        assert step.captured_output["output1"] == "value1"
        mock_temp_file.assert_called_once()
        mock_popen.assert_called_once()
        mock_remove.assert_called_once_with("/tmp/test_file")

    @patch("tempfile.NamedTemporaryFile")
    @patch("subprocess.Popen")
    @patch("os.remove")
    def test_run_command_with_error(self, mock_remove, mock_popen, mock_temp_file):
        # Setup
        mock_file = MagicMock()
        mock_temp_file.return_value = mock_file
        mock_file.name = "/tmp/test_file"

        mock_process = MagicMock()
        mock_process.stdout.readline.side_effect = ["Output line 1\n", ""]
        mock_process.stderr.readline.side_effect = ["Error line 1\n", ""]
        mock_process.poll.side_effect = [None, None, 1]
        mock_process.wait.return_value = 1
        mock_popen.return_value = mock_process

        step = Step(id="test-step", command="echo", arguments=["Hello", "World"])

        # Execute
        result = step.run()

        # Verify
        assert result == StepStatus.ERROR
        assert step.status == StepStatus.ERROR
        mock_temp_file.assert_called_once()
        mock_popen.assert_called_once()
        mock_remove.assert_called_once_with("/tmp/test_file")

    def test_run_with_dry_run(self):
        # Setup
        step = Step(id="test-step", command="echo", arguments=["Hello", "World"])

        # Execute
        result = step.run(dry=True)

        # Verify
        assert result == StepStatus.DRY_RUN
        assert step.status == StepStatus.DRY_RUN

    def test_run_with_skipped_step(self):
        # Setup
        step = Step(id="test-step", command="echo", arguments=["Hello", "World"])
        step.skipped = True

        # Execute
        result = step.run()

        # Verify
        assert result == StepStatus.SKIPPED_BY_USER
        assert step.status == StepStatus.SKIPPED_BY_USER

    def test_run_with_previous_errors(self):
        # Setup
        step = Step(id="test-step", command="echo", arguments=["Hello", "World"])

        # Execute
        result = step.run(previous={"step1": StepStatus.ERROR})

        # Verify
        assert result == StepStatus.SKIPPED_AFTER_FAILURE
        assert step.status == StepStatus.SKIPPED_AFTER_FAILURE

    @patch("tempfile.NamedTemporaryFile")
    @patch("subprocess.Popen")
    @patch("os.remove")
    def test_run_with_input_data(self, mock_remove, mock_popen, mock_temp_file):
        # Setup
        mock_file = MagicMock()
        mock_temp_file.return_value = mock_file
        mock_file.name = "/tmp/test_file"

        mock_process = MagicMock()
        mock_process.stdout.readline.side_effect = ["Output line 1\n", ""]
        mock_process.stderr.readline.side_effect = [""]
        mock_process.poll.side_effect = [None, None, 0]
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process

        step = Step(
            id="test-step",
            command="echo",
            arguments=["Hello", "World"],
            inputs={"input1": {"as": "INPUT_VAR1", "stepId": "step1", "output": "output1"}},
        )

        # Execute
        result = step.run(input_data={"input1": "input_value1"})

        # Verify
        assert result == StepStatus.SUCCESS
        mock_popen.assert_called_once()
        # Check that environment variables were set correctly
        env = mock_popen.call_args[1]["env"]
        assert "INPUT_VAR1" in env
        assert env["INPUT_VAR1"] == "input_value1"

    @patch("tempfile.NamedTemporaryFile")
    @patch("subprocess.Popen")
    @patch("os.remove")
    def test_run_with_missing_required_input(self, mock_remove, mock_popen, mock_temp_file):
        # Setup
        step = Step(
            id="test-step",
            command="echo",
            arguments=["Hello", "World"],
            inputs={"input1": {"as": "INPUT_VAR1", "stepId": "step1", "output": "output1", "optional": False}},
        )

        # Execute and verify
        with pytest.raises(ValueError):
            step.run(input_data={})

    @patch("tempfile.NamedTemporaryFile")
    @patch("subprocess.Popen")
    @patch("os.remove")
    def test_run_with_default_input_value(self, mock_remove, mock_popen, mock_temp_file):
        # Setup
        mock_file = MagicMock()
        mock_temp_file.return_value = mock_file
        mock_file.name = "/tmp/test_file"

        mock_process = MagicMock()
        mock_process.stdout.readline.side_effect = ["Output line 1\n", ""]
        mock_process.stderr.readline.side_effect = [""]
        mock_process.poll.side_effect = [None, None, 0]
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process

        step = Step(
            id="test-step",
            command="echo",
            arguments=["Hello", "World"],
            inputs={
                "input1": {"as": "INPUT_VAR1", "stepId": "step1", "output": "output1", "defaultValue": "default_value"}
            },
        )

        # Execute
        result = step.run(input_data={})

        # Verify
        assert result == StepStatus.SUCCESS
        # Check that environment variables were set correctly
        env = mock_popen.call_args[1]["env"]
        assert "INPUT_VAR1" in env
        assert env["INPUT_VAR1"] == "default_value"

    def test_check_env_returns_required_env_vars(self):
        # Setup
        env_var1 = MagicMock()
        env_var1.is_required.return_value = True
        env_var1.effective_value.return_value = None
        env_var1.description = "Required var 1"

        env_var2 = MagicMock()
        env_var2.is_required.return_value = False

        step = Step(id="test-step", command="echo")
        step.environment = {"ENV_VAR1": env_var1, "ENV_VAR2": env_var2}

        # Execute
        result = step.check_env()

        # Verify
        assert "ENV_VAR1" in result
        assert result["ENV_VAR1"] == "Required var 1"
        assert "ENV_VAR2" not in result

    def test_check_env_returns_empty_dict_for_skipped_step(self):
        # Setup
        env_var1 = MagicMock()
        env_var1.is_required.return_value = True

        step = Step(id="test-step", command="echo")
        step.environment = {"ENV_VAR1": env_var1}
        step.skipped = True

        # Execute
        result = step.check_env()

        # Verify
        assert result == {}

    def test_simple_repr(self):
        # Setup
        step = Step(id="test-step", command="echo", description="Test step")
        step.status = StepStatus.SUCCESS

        # Execute
        result = step.simple_repr()

        # Verify
        assert "test-step" in result
        assert StepStatus.SUCCESS.name in result
        assert "Test step" in result

    def test_str_representation(self):
        # Setup
        step = Step(
            id="test-step",
            command="echo",
            arguments=["Hello", "World"],
            description="Test step",
            environment={"TEST_VAR": {"value": "test_value", "description": "Test var"}},
            useSystemEnvironment=True,
        )
        step.status = StepStatus.SUCCESS

        # Execute
        result = str(step)

        # Verify
        assert "test-step" in result
        assert "echo Hello World" in result
        assert "Test step" in result
        assert "TEST_VAR" in result
        assert "Test var" in result
        assert StepStatus.SUCCESS.name in result


class TestOutputParser:
    def test_run_parses_output_data(self):
        # Setup
        mock_stream = MagicMock()
        mock_stream.readline.side_effect = [
            "Regular output\n",
            "CSM-OUTPUT-DATA:output1:value1\n",
            "CSM-OUTPUT-DATA:output2:value2\n",
            "",
        ]

        output_queue = queue.Queue()

        # Execute
        parser = Step.OutputParser(mock_stream, output_queue)
        parser.run()

        # Verify
        assert parser.outputs == {"output1": "value1", "output2": "value2"}
        assert output_queue.qsize() == 1
        is_stderr, line = output_queue.get()
        assert is_stderr is False
        assert line == "Regular output"

    def test_run_handles_malformed_output_data(self):
        # Setup
        mock_stream = MagicMock()
        mock_stream.readline.side_effect = ["CSM-OUTPUT-DATA:malformed\n", "CSM-OUTPUT-DATA:output1:value1\n", ""]

        output_queue = queue.Queue()

        # Execute
        parser = Step.OutputParser(mock_stream, output_queue)
        parser.run()

        # Verify
        assert parser.outputs == {"output1": "value1"}
        assert output_queue.qsize() == 0

    def test_run_ignores_output_data_in_stderr(self):
        # Setup
        mock_stream = MagicMock()
        mock_stream.readline.side_effect = ["CSM-OUTPUT-DATA:output1:value1\n", ""]

        output_queue = queue.Queue()

        # Execute
        parser = Step.OutputParser(mock_stream, output_queue, is_stderr=True)
        parser.run()

        # Verify
        assert parser.outputs == {}
        assert output_queue.qsize() == 1
        is_stderr, line = output_queue.get()
        assert is_stderr is True
        assert line == "CSM-OUTPUT-DATA:output1:value1"

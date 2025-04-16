import pytest
from unittest.mock import MagicMock, patch, mock_open
import os
import configparser
import subprocess
from pathlib import Path
import sys
import logging

from cosmotech.orchestrator.api.entrypoint import (
    get_entrypoint_env,
    get_simulator_executable_name,
    run_direct_simulator,
    setup_loki_logging,
    run_template_with_id,
    run_entrypoint,
    EntrypointException,
)


class TestGetEntrypointEnv:
    @patch("configparser.ConfigParser.read")
    @patch("configparser.ConfigParser.has_section")
    @patch("configparser.ConfigParser.items")
    def test_returns_env_vars_when_section_exists(self, mock_items, mock_has_section, mock_read):
        # Setup
        mock_has_section.return_value = True
        mock_items.return_value = [("test_key", "test_value"), ("another_key", "another_value")]

        # Execute
        result = get_entrypoint_env()

        # Verify
        assert mock_read.called_with("/pkg/share/project.csm")
        assert "TEST_KEY" in result
        assert result["TEST_KEY"] == "test_value"
        assert "ANOTHER_KEY" in result
        assert result["ANOTHER_KEY"] == "another_value"

    @patch("configparser.ConfigParser.read")
    @patch("configparser.ConfigParser.has_section")
    def test_returns_empty_dict_when_section_not_exists(self, mock_has_section, mock_read):
        # Setup
        mock_has_section.return_value = False

        # Execute
        result = get_entrypoint_env()

        # Verify
        assert mock_read.called_with("/pkg/share/project.csm")
        assert result == {}


class TestGetSimulatorExecutableName:
    @patch("cosmotech.orchestrator.api.entrypoint.which")
    def test_returns_csm_simulator_when_available(self, mock_which):
        # Setup
        mock_which.side_effect = lambda x: "/path/to/simulator" if x == "csm-simulator" else None

        # Execute
        result = get_simulator_executable_name()

        # Verify
        assert result == "csm-simulator"

    @patch("cosmotech.orchestrator.api.entrypoint.which")
    def test_returns_main_when_csm_simulator_not_available(self, mock_which):
        # Setup
        mock_which.side_effect = lambda x: None if x == "csm-simulator" else "/path/to/main"

        # Execute
        result = get_simulator_executable_name()

        # Verify
        assert result == "main"


class TestRunDirectSimulator:
    @patch("cosmotech.orchestrator.api.entrypoint.get_simulator_executable_name")
    @patch("subprocess.check_call")
    @patch.dict(os.environ, {"CSM_SIMULATION": "test_simulation"})
    def test_with_simulation_env_var(self, mock_check_call, mock_get_simulator):
        # Setup
        mock_get_simulator.return_value = "csm-simulator"
        mock_check_call.return_value = 0

        # Execute
        result = run_direct_simulator()

        # Verify
        mock_check_call.assert_called_once_with(["csm-simulator", "-i", "test_simulation"])
        assert result == 0

    @patch("cosmotech.orchestrator.api.entrypoint.get_simulator_executable_name")
    @patch("subprocess.check_call")
    @patch.dict(os.environ, {"CSM_SIMULATION": "test_simulation", "CSM_PROBES_MEASURES_TOPIC": "test_topic"})
    def test_with_probes_topic(self, mock_check_call, mock_get_simulator):
        # Setup
        mock_get_simulator.return_value = "csm-simulator"
        mock_check_call.return_value = 0

        # Execute
        result = run_direct_simulator()

        # Verify
        mock_check_call.assert_called_once_with(
            ["csm-simulator", "-i", "test_simulation", "--amqp-consumer", "test_topic"]
        )
        assert result == 0

    @patch("cosmotech.orchestrator.api.entrypoint.get_simulator_executable_name")
    @patch("subprocess.check_call")
    @patch.dict(os.environ, {}, clear=True)
    @patch("sys.argv", ["entrypoint.py", "arg1", "arg2"])
    def test_without_simulation_env_var_entrypoint_py(self, mock_check_call, mock_get_simulator):
        # Setup
        mock_get_simulator.return_value = "csm-simulator"
        mock_check_call.return_value = 0

        # Execute
        result = run_direct_simulator()

        # Verify
        mock_check_call.assert_called_once_with(["csm-simulator", "arg1", "arg2"])
        assert result == 0

    @patch("cosmotech.orchestrator.api.entrypoint.get_simulator_executable_name")
    @patch("subprocess.check_call")
    @patch.dict(os.environ, {}, clear=True)
    @patch("sys.argv", ["other_script.py", "command", "arg1", "arg2"])
    def test_without_simulation_env_var_other_script(self, mock_check_call, mock_get_simulator):
        # Setup
        mock_get_simulator.return_value = "csm-simulator"
        mock_check_call.return_value = 0

        # Execute
        result = run_direct_simulator()

        # Verify
        mock_check_call.assert_called_once_with(["csm-simulator", "arg1", "arg2"])
        assert result == 0

    @patch("cosmotech.orchestrator.api.entrypoint.get_simulator_executable_name")
    @patch("subprocess.check_call")
    @patch.dict(os.environ, {"CSM_SIMULATION": "test_simulation"})
    def test_handles_subprocess_error(self, mock_check_call, mock_get_simulator):
        # Setup
        mock_get_simulator.return_value = "csm-simulator"
        error = subprocess.CalledProcessError(1, "csm-simulator")
        mock_check_call.side_effect = error

        # Execute
        result = run_direct_simulator()

        # Verify
        assert result == 1


class TestSetupLokiLogging:
    @patch.dict(
        os.environ,
        {
            "CSM_LOKI_URL": "http://loki:3100",
            "CSM_ORGANIZATION_ID": "org1",
            "CSM_WORKSPACE_ID": "ws1",
            "CSM_RUNNER_ID": "runner1",
            "CSM_RUN_ID": "run1",
            "CSM_NAMESPACE_NAME": "namespace1",
            "ARGO_CONTAINER_NAME": "container1",
            "ARGO_NODE_ID": "node1",
        },
    )
    def test_setup_with_loki_url(self):
        import logging_loki

        setup_loki_logging()
        LOGGER = logging.getLogger("csm.run.entrypoint")

        assert isinstance(LOGGER.handlers.pop(), logging_loki.LokiHandler)

    @patch("importlib.import_module")
    @patch.dict(os.environ, {}, clear=True)
    def test_no_setup_without_loki_url(self, mock_importlib):
        # Execute
        setup_loki_logging()

        # Verify
        mock_importlib.assert_not_called()


class TestRunTemplateWithId:
    @patch("subprocess.Popen")
    @patch("importlib.util.find_spec")
    @patch("pathlib.Path.is_file")
    def test_successful_run(self, mock_is_file, mock_find_spec, mock_popen):
        # Setup
        mock_find_spec.return_value = MagicMock()
        mock_is_file.return_value = True

        mock_process = MagicMock()
        mock_process.stdout.readline.side_effect = ["INFO log line\n", "ERROR log line\n", "DEBUG log line\n", ""]
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process

        # Execute
        result = run_template_with_id("test_template")

        # Verify
        assert result == 0
        mock_popen.assert_called_once()
        assert mock_popen.call_args[0][0] == ["csm-orc", "run", "/pkg/share/code/run_templates/test_template/run.json"]

    @patch("importlib.util.find_spec")
    def test_missing_library(self, mock_find_spec):
        # Setup
        mock_find_spec.return_value = None

        # Execute and verify
        with pytest.raises(EntrypointException):
            run_template_with_id("test_template")

    @patch("importlib.util.find_spec")
    @patch("pathlib.Path.is_file")
    def test_missing_run_json(self, mock_is_file, mock_find_spec):
        # Setup
        mock_find_spec.return_value = MagicMock()
        mock_is_file.return_value = False

        # Execute and verify
        with pytest.raises(EntrypointException):
            run_template_with_id("test_template")


class TestRunEntrypoint:
    @patch("cosmotech.orchestrator.api.entrypoint.setup_loki_logging")
    @patch("cosmotech.orchestrator.api.entrypoint.get_entrypoint_env")
    @patch("cosmotech.orchestrator.api.entrypoint.run_direct_simulator")
    @patch.dict(os.environ, {}, clear=True)
    def test_run_direct_simulator_when_no_template(self, mock_run_simulator, mock_get_env, mock_setup_loki):
        # Setup
        mock_run_simulator.return_value = 0

        # Execute
        result = run_entrypoint()

        # Verify
        mock_setup_loki.assert_called_once()
        mock_get_env.assert_called_once()
        mock_run_simulator.assert_called_once()
        assert result == 0

    @patch("cosmotech.orchestrator.api.entrypoint.setup_loki_logging")
    @patch("cosmotech.orchestrator.api.entrypoint.get_entrypoint_env")
    @patch("cosmotech.orchestrator.api.entrypoint.run_template_with_id")
    @patch.dict(os.environ, {"CSM_RUN_TEMPLATE_ID": "test_template"})
    def test_run_template_when_template_id_provided(self, mock_run_template, mock_get_env, mock_setup_loki):
        # Setup
        mock_run_template.return_value = 0

        # Execute
        result = run_entrypoint()

        # Verify
        mock_setup_loki.assert_called_once()
        mock_get_env.assert_called_once()
        mock_run_template.assert_called_once_with("test_template")
        assert result == 0

    @patch("cosmotech.orchestrator.api.entrypoint.setup_loki_logging")
    @patch("cosmotech.orchestrator.api.entrypoint.get_entrypoint_env")
    @patch("cosmotech.orchestrator.api.entrypoint.run_template_with_id")
    @patch.dict(os.environ, {"CSM_RUN_TEMPLATE_ID": "test_template"})
    def test_handles_entrypoint_exception(self, mock_run_template, mock_get_env, mock_setup_loki):
        # Setup
        mock_run_template.side_effect = EntrypointException("Test error")

        # Execute
        result = run_entrypoint()

        # Verify
        assert result == 1

    @patch("cosmotech.orchestrator.api.entrypoint.setup_loki_logging")
    @patch("cosmotech.orchestrator.api.entrypoint.get_entrypoint_env")
    @patch("cosmotech.orchestrator.api.entrypoint.run_template_with_id")
    @patch.dict(os.environ, {"CSM_RUN_TEMPLATE_ID": "test_template"})
    def test_handles_subprocess_error(self, mock_run_template, mock_get_env, mock_setup_loki):
        # Setup
        mock_run_template.side_effect = subprocess.CalledProcessError(1, "test")

        # Execute
        result = run_entrypoint()

        # Verify
        assert result == 1

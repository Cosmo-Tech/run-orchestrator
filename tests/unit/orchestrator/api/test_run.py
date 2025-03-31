from unittest.mock import MagicMock
from unittest.mock import mock_open
from unittest.mock import patch

import pytest

from cosmotech.orchestrator.api.run import display_environment
from cosmotech.orchestrator.api.run import generate_env_file
from cosmotech.orchestrator.api.run import run_template
from cosmotech.orchestrator.api.run import validate_template


class TestValidateTemplate:
    @patch("cosmotech.orchestrator.api.run.Orchestrator")
    def test_returns_true_for_valid_template(self, mock_orchestrator_class):
        # Setup
        mock_orchestrator = MagicMock()
        mock_orchestrator_class.return_value = mock_orchestrator

        # Execute
        result = validate_template("valid_template.json")

        # Verify
        mock_orchestrator.load_json_file.assert_called_once_with("valid_template.json", validate_only=True)
        assert result is True

    @patch("cosmotech.orchestrator.api.run.Orchestrator")
    def test_returns_false_for_invalid_template(self, mock_orchestrator_class):
        # Setup
        mock_orchestrator = MagicMock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.load_json_file.side_effect = ValueError("Invalid template")

        # Execute
        result = validate_template("invalid_template.json")

        # Verify
        mock_orchestrator.load_json_file.assert_called_once_with("invalid_template.json", validate_only=True)
        assert result is False


class TestDisplayEnvironment:
    @patch("cosmotech.orchestrator.api.run.Orchestrator")
    def test_displays_environment_for_valid_template(self, mock_orchestrator_class):
        # Setup
        mock_orchestrator = MagicMock()
        mock_orchestrator_class.return_value = mock_orchestrator

        # Execute
        result = display_environment("valid_template.json")

        # Verify
        mock_orchestrator.load_json_file.assert_called_once_with("valid_template.json", display_env=True)
        assert result == {}

    @patch("cosmotech.orchestrator.api.run.Orchestrator")
    def test_raises_error_for_invalid_template(self, mock_orchestrator_class):
        # Setup
        mock_orchestrator = MagicMock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.load_json_file.side_effect = ValueError("Invalid template")

        # Execute and verify
        with pytest.raises(ValueError, match="Invalid template"):
            display_environment("invalid_template.json")


class TestGenerateEnvFile:
    @patch("cosmotech.orchestrator.api.run.Orchestrator")
    @patch("pathlib.Path.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    def test_generates_env_file_for_valid_template(self, mock_mkdir, mock_file, mock_orchestrator_class):
        # Setup
        mock_orchestrator = MagicMock()
        mock_orchestrator_class.return_value = mock_orchestrator

        # Mock environment variables
        mock_env_var1 = MagicMock()
        mock_env_var1.description = "Env var 1 description"
        mock_env_var1.effective_value.return_value = "value1"

        mock_env_var2 = MagicMock()
        mock_env_var2.description = "Env var 2 description"
        mock_env_var2.effective_value.return_value = None

        # Mock step with environment variables
        mock_step = MagicMock()
        mock_step.environment = {"ENV_VAR1": mock_env_var1, "ENV_VAR2": mock_env_var2}

        # Mock orchestrator response
        mock_orchestrator.load_json_file.return_value = ({"step1": (mock_step, None)}, None)

        # Execute
        result = generate_env_file("valid_template.json", "output.env")

        # Verify
        mock_orchestrator.load_json_file.assert_called_once_with("valid_template.json", display_env=True)
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_file().writelines.assert_called_once()
        assert result is True

    @patch("cosmotech.orchestrator.api.run.Orchestrator")
    def test_returns_false_for_invalid_template(self, mock_orchestrator_class):
        # Setup
        mock_orchestrator = MagicMock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.load_json_file.side_effect = ValueError("Invalid template")

        # Execute
        result = generate_env_file("invalid_template.json", "output.env")

        # Verify
        assert result is False


class TestRunTemplate:
    @patch("cosmotech.orchestrator.api.run.Orchestrator")
    def test_returns_false_for_invalid_template(self, mock_orchestrator_class):
        # Setup
        mock_orchestrator = MagicMock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.load_json_file.side_effect = ValueError("Invalid template")

        # Execute
        success, results = run_template("invalid_template.json")

        # Verify
        assert success is False
        assert results is None
        mock_orchestrator.load_json_file.assert_called_once_with("invalid_template.json", False, False, [])

    @patch("cosmotech.orchestrator.api.run.Orchestrator")
    def test_returns_true_when_graph_is_none(self, mock_orchestrator_class):
        # Setup
        mock_orchestrator = MagicMock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.load_json_file.return_value = (MagicMock(), None)

        # Execute
        success, results = run_template("valid_template.json")

        # Verify
        assert success is True
        assert results is None

    @patch("cosmotech.orchestrator.api.run.Orchestrator")
    def test_successful_run_with_all_steps_done(self, mock_orchestrator_class):
        # Setup
        mock_orchestrator = MagicMock()
        mock_orchestrator_class.return_value = mock_orchestrator

        # Create mock steps and graph
        mock_step1 = MagicMock()
        mock_step1.status = "Done"
        mock_step1.simple_repr.return_value = "Step 1 Done"

        mock_step2 = MagicMock()
        mock_step2.status = "Done"
        mock_step2.simple_repr.return_value = "Step 2 Done"

        mock_graph = MagicMock()

        # Setup return value for load_json_file
        mock_orchestrator.load_json_file.return_value = (
            {"step1": (mock_step1, None), "step2": (mock_step2, None)},
            mock_graph,
        )

        # Execute
        success, results = run_template("valid_template.json")

        # Verify
        assert success is True
        assert "step1" in results
        assert "step2" in results
        assert results["step1"] == mock_step1
        assert results["step2"] == mock_step2
        mock_graph.evaluate.assert_called_once_with(mode="threading")

    @patch("cosmotech.orchestrator.api.run.Orchestrator")
    def test_run_with_error_step(self, mock_orchestrator_class):
        # Setup
        mock_orchestrator = MagicMock()
        mock_orchestrator_class.return_value = mock_orchestrator

        # Create mock steps and graph
        mock_step1 = MagicMock()
        mock_step1.status = "Done"
        mock_step1.simple_repr.return_value = "Step 1 Done"

        mock_step2 = MagicMock()
        mock_step2.status = "RunError"
        mock_step2.simple_repr.return_value = "Step 2 Error"

        mock_graph = MagicMock()

        # Setup return value for load_json_file
        mock_orchestrator.load_json_file.return_value = (
            {"step1": (mock_step1, None), "step2": (mock_step2, None)},
            mock_graph,
        )

        # Execute
        success, results = run_template("valid_template.json")

        # Verify
        assert success is False
        assert "step1" in results
        assert "step2" in results
        assert results["step1"] == mock_step1
        assert results["step2"] == mock_step2
        mock_graph.evaluate.assert_called_once_with(mode="threading")

    @patch("cosmotech.orchestrator.api.run.Orchestrator")
    @patch("cosmotech.orchestrator.templates.library.Library")
    @patch("cosmotech.orchestrator.api.run.Step")
    def test_run_with_exit_handlers(self, mock_step_class, mock_library_class, mock_orchestrator_class):
        # Setup
        mock_orchestrator = MagicMock()
        mock_orchestrator_class.return_value = mock_orchestrator

        # Create mock steps and graph
        mock_step1 = MagicMock()
        mock_step1.status = "Done"
        mock_step1.simple_repr.return_value = "Step 1 Done"

        mock_graph = MagicMock()

        # Setup return value for load_json_file
        mock_orchestrator.load_json_file.return_value = ({"step1": (mock_step1, None)}, mock_graph)

        # Setup Library mock
        mock_library = MagicMock()
        mock_library_class.return_value = mock_library
        mock_library.list_exit_commands.return_value = ["exit_handler1", "exit_handler2"]
        mock_step_exit1 = MagicMock()
        mock_step_exit2 = MagicMock()
        mock_step_class.side_effect = [mock_step_exit1, mock_step_exit2]
        mock_step_exit1.run.return_value = True
        mock_step_exit2.run.return_value = True

        # Execute
        success, results = run_template("valid_template.json", exit_handlers=True)
        # Verify
        assert success is True
        assert "step1" in results
        assert results["step1"] == mock_step1

        # Verify exit handlers were created and run
        mock_step_class.assert_any_call(
            id="exit_handler1", commandId="exit_handler1", environment={"CSM_ORC_IS_SUCCESS": {"value": "True"}}
        )
        mock_step_class.assert_any_call(
            id="exit_handler2", commandId="exit_handler2", environment={"CSM_ORC_IS_SUCCESS": {"value": "True"}}
        )

    @patch("cosmotech.orchestrator.api.run.Orchestrator")
    def test_run_with_dry_run_flag(self, mock_orchestrator_class):
        # Setup
        mock_orchestrator = MagicMock()
        mock_orchestrator_class.return_value = mock_orchestrator

        # Create mock steps and graph
        mock_step1 = MagicMock()
        mock_step1.status = "DryRun"
        mock_step1.simple_repr.return_value = "Step 1 DryRun"

        mock_graph = MagicMock()

        # Setup return value for load_json_file
        mock_orchestrator.load_json_file.return_value = ({"step1": (mock_step1, None)}, mock_graph)

        # Execute
        success, results = run_template("valid_template.json", dry_run=True)

        # Verify
        assert success is True
        assert "step1" in results
        assert results["step1"] == mock_step1
        mock_orchestrator.load_json_file.assert_called_once_with("valid_template.json", True, False, [])

    @patch("cosmotech.orchestrator.api.run.Orchestrator")
    def test_run_with_display_env_flag(self, mock_orchestrator_class):
        # Setup
        mock_orchestrator = MagicMock()
        mock_orchestrator_class.return_value = mock_orchestrator

        # Create mock steps and graph
        mock_step1 = MagicMock()
        mock_step1.status = "Done"
        mock_step1.simple_repr.return_value = "Step 1 Done"

        mock_graph = MagicMock()

        # Setup return value for load_json_file
        mock_orchestrator.load_json_file.return_value = ({"step1": (mock_step1, None)}, mock_graph)

        # Execute
        success, results = run_template("valid_template.json", display_env=True)

        # Verify
        assert success is True
        assert "step1" in results
        assert results["step1"] == mock_step1
        mock_orchestrator.load_json_file.assert_called_once_with("valid_template.json", False, True, [])

    @patch("cosmotech.orchestrator.api.run.Orchestrator")
    def test_run_with_skipped_steps(self, mock_orchestrator_class):
        # Setup
        mock_orchestrator = MagicMock()
        mock_orchestrator_class.return_value = mock_orchestrator

        # Create mock steps and graph
        mock_step1 = MagicMock()
        mock_step1.status = "Done"
        mock_step1.simple_repr.return_value = "Step 1 Done"

        mock_step2 = MagicMock()
        mock_step2.status = "Skipped"
        mock_step2.simple_repr.return_value = "Step 2 Skipped"

        mock_graph = MagicMock()

        # Setup return value for load_json_file
        mock_orchestrator.load_json_file.return_value = (
            {"step1": (mock_step1, None), "step2": (mock_step2, None)},
            mock_graph,
        )

        # Execute
        success, results = run_template("valid_template.json", skipped_steps=["step2"])

        # Verify
        assert success is True
        assert "step1" in results
        assert "step2" in results
        assert results["step1"] == mock_step1
        assert results["step2"] == mock_step2
        mock_orchestrator.load_json_file.assert_called_once_with("valid_template.json", False, False, ["step2"])

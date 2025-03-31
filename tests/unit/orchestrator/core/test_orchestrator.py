from unittest.mock import MagicMock
from unittest.mock import mock_open
from unittest.mock import patch

import pytest

from cosmotech.orchestrator.core.orchestrator import FileLoader
from cosmotech.orchestrator.core.orchestrator import Orchestrator
from cosmotech.orchestrator.core.step import Step


class TestFileLoader:
    def test_load_step_creates_step_from_dict(self):
        # Setup
        container = {}
        step_dict = {
            "id": "test-step",
            "command": "echo",
            "arguments": ["Hello", "World"],
            "environment": {"TEST_VAR": {"value": "test_value"}},
        }

        # Execute
        result = FileLoader.load_step(container, **step_dict)

        # Verify
        assert isinstance(result, Step)
        assert result.id == "test-step"
        assert result.command == "echo"
        assert result.arguments == ["Hello", "World"]
        assert "TEST_VAR" in result.environment
        assert container["test-step"] == result

    def test_load_step_raises_error_when_step_already_exists(self):
        # Setup
        container = {"test-step": MagicMock()}
        step_dict = {"id": "test-step", "command": "echo"}

        # Execute and verify
        with pytest.raises(ValueError):
            FileLoader.load_step(container, **step_dict)

    def test_load_step_allows_override(self):
        # Setup
        container = {"test-step": MagicMock()}
        step_dict = {"id": "test-step", "command": "echo"}

        # Execute
        result = FileLoader.load_step(container, override=True, **step_dict)

        # Verify
        assert container["test-step"] == result

    @patch("json.load")
    @patch("pathlib.Path.open", new_callable=mock_open)
    @patch("jsonschema.validate")
    @patch("cosmotech.orchestrator.core.orchestrator.FileLoader.load_step")
    @patch("cosmotech.orchestrator.templates.plugin.Plugin.register_template")
    @patch("cosmotech.orchestrator.templates.library.Library.load_plugin")
    def test_call_loads_steps_from_file(
        self, mock_load_plugin, mock_register_template, mock_load_step, mock_validate, mock_file, mock_json_load
    ):
        # Setup
        file_path = "test_file.json"
        mock_json_load.return_value = {
            "commandTemplates": [{"id": "template1", "command": "echo"}, {"id": "template2", "command": "ls"}],
            "steps": [{"id": "step1", "commandId": "template1"}, {"id": "step2", "commandId": "template2"}],
        }

        # Mock step creation
        mock_step1 = MagicMock()
        mock_step1.id = "step1"
        mock_step2 = MagicMock()
        mock_step2.id = "step2"
        mock_load_step.side_effect = [mock_step1, mock_step2]

        # Create file loader
        file_loader = FileLoader(file_path)

        # Execute
        result = file_loader()

        # Verify
        assert mock_json_load.called
        assert mock_validate.called
        assert mock_register_template.call_count == 2
        assert mock_load_plugin.called
        assert mock_load_step.call_count == 2
        assert "step1" in result
        assert "step2" in result
        assert result["step1"] == mock_step1
        assert result["step2"] == mock_step2

    @patch("json.load")
    @patch("pathlib.Path.open", new_callable=mock_open)
    @patch("jsonschema.validate")
    @patch("cosmotech.orchestrator.core.orchestrator.FileLoader.load_step")
    def test_call_with_skipped_steps(self, mock_load_step, mock_validate, mock_file, mock_json_load):
        # Setup
        file_path = "test_file.json"
        mock_json_load.return_value = {
            "commandTemplates": [],
            "steps": [{"id": "step1", "command": "echo"}, {"id": "step2", "command": "ls"}],
        }

        # Mock step creation
        from cosmotech.orchestrator.core.step import Step

        mock_step1 = MagicMock(Step)
        mock_step1.id = "step1"
        mock_step1.skipped = False
        mock_step2 = MagicMock(Step)
        mock_step2.id = "step2"
        mock_step2.skipped = False
        mock_load_step.side_effect = [mock_step1, mock_step2]

        # Create file loader
        file_loader = FileLoader(file_path)

        # Execute
        result = file_loader(skipped_steps=["step1"])

        # Verify
        assert mock_step1.skipped is True
        assert mock_step2.skipped is False


class TestOrchestrator:
    @patch("cosmotech.orchestrator.core.orchestrator.FileLoader")
    @patch("cosmotech.orchestrator.templates.library.Library.display_library")
    def test_load_json_file_for_validation_only(self, mock_display_library, mock_file_loader_class):
        # Setup
        mock_file_loader = MagicMock()
        mock_file_loader_class.return_value = mock_file_loader
        mock_file_loader.return_value = {}

        orchestrator = Orchestrator()

        # Execute
        result = orchestrator.load_json_file("test_file.json", validate_only=True)

        # Verify
        mock_file_loader_class.assert_called_once_with("test_file.json")
        mock_file_loader.assert_called_once_with(skipped_steps=())
        mock_display_library.assert_called_once()
        assert result == (None, None)

    @patch("cosmotech.orchestrator.core.orchestrator.FileLoader")
    @patch("cosmotech.orchestrator.templates.library.Library.display_library")
    def test_load_json_file_with_dry_run(self, mock_display_library, mock_file_loader_class):
        # Setup
        mock_file_loader = MagicMock()
        mock_file_loader_class.return_value = mock_file_loader

        # Create mock steps
        mock_step1 = MagicMock()
        mock_step1.id = "step1"
        mock_step1.precedents = []

        mock_file_loader.return_value = {"step1": mock_step1}

        orchestrator = Orchestrator()

        # Execute
        steps, graph = orchestrator.load_json_file("test_file.json", dry=True, ignore_error=True)

        # Verify
        mock_file_loader_class.assert_called_once_with("test_file.json")
        mock_file_loader.assert_called_once_with(skipped_steps=())
        assert "step1" in steps
        assert steps["step1"][0] == mock_step1
        assert graph is not None

    @patch("cosmotech.orchestrator.core.orchestrator.FileLoader")
    @patch("cosmotech.orchestrator.templates.library.Library.display_library")
    def test_load_json_file_with_display_env(self, mock_display_library, mock_file_loader_class):
        # Setup
        mock_file_loader = MagicMock()
        mock_file_loader_class.return_value = mock_file_loader

        # Create mock steps
        mock_step1 = MagicMock()
        mock_step1.id = "step1"
        mock_step1.precedents = []
        mock_step1.check_env.return_value = {}

        mock_file_loader.return_value = {"step1": mock_step1}

        orchestrator = Orchestrator()

        # Execute
        steps, graph = orchestrator.load_json_file("test_file.json", display_env=True)

        # Verify
        mock_file_loader_class.assert_called_once_with("test_file.json")
        mock_file_loader.assert_called_once_with(skipped_steps=())
        assert "step1" in steps
        assert steps["step1"][0] == mock_step1
        assert graph is not None

    @patch("cosmotech.orchestrator.core.orchestrator.FileLoader")
    @patch("cosmotech.orchestrator.templates.library.Library.display_library")
    def test_load_json_file_with_missing_env_vars(self, mock_display_library, mock_file_loader_class):
        # Setup
        mock_file_loader = MagicMock()
        mock_file_loader_class.return_value = mock_file_loader

        # Create mock steps
        mock_step1 = MagicMock()
        mock_step1.id = "step1"
        mock_step1.precedents = []
        mock_step1.check_env.return_value = {"TEST_VAR": "Required variable"}

        mock_file_loader.return_value = {"step1": mock_step1}

        orchestrator = Orchestrator()

        # Execute and verify
        with pytest.raises(ValueError):
            orchestrator.load_json_file("test_file.json")

    @patch("cosmotech.orchestrator.core.orchestrator.FileLoader")
    @patch("cosmotech.orchestrator.templates.library.Library.display_library")
    def test_load_json_file_with_ignore_error(self, mock_display_library, mock_file_loader_class):
        # Setup
        mock_file_loader = MagicMock()
        mock_file_loader_class.return_value = mock_file_loader

        # Create mock steps
        mock_step1 = MagicMock()
        mock_step1.id = "step1"
        mock_step1.precedents = []
        mock_step1.check_env.return_value = {"TEST_VAR": "Required variable"}

        mock_file_loader.return_value = {"step1": mock_step1}

        orchestrator = Orchestrator()

        # Execute
        steps, graph = orchestrator.load_json_file("test_file.json", ignore_error=True)

        # Verify
        assert "step1" in steps
        assert steps["step1"][0] == mock_step1
        assert graph is not None

    @patch("flowpipe.Graph")
    def test_load_from_json_content(self, mock_graph_class):
        # Setup
        mock_graph = MagicMock()
        mock_graph_class.return_value = mock_graph

        # Create mock steps
        mock_step1 = MagicMock()
        mock_step1.id = "step1"
        mock_step1.precedents = []
        mock_step1.check_env.return_value = {}

        mock_step2 = MagicMock()
        mock_step2.id = "step2"
        mock_step2.precedents = ["step1"]
        mock_step2.check_env.return_value = {}
        mock_step2.inputs = {}

        steps = {"step1": mock_step1, "step2": mock_step2}

        # Execute
        result_steps, result_graph = Orchestrator._load_from_json_content("test_file.json", steps)

        # Verify
        assert "step1" in result_steps
        assert "step2" in result_steps
        assert result_graph == mock_graph

    @patch("flowpipe.Graph")
    def test_load_from_json_content_with_data_flow(self, mock_graph_class):
        # Setup
        mock_graph = MagicMock()
        mock_graph_class.return_value = mock_graph

        # Create mock steps
        mock_step1 = MagicMock()
        mock_step1.id = "step1"
        mock_step1.precedents = []
        mock_step1.check_env.return_value = {}
        mock_step1.outputs = {"output1": {}}

        mock_step2 = MagicMock()
        mock_step2.id = "step2"
        mock_step2.precedents = ["step1"]
        mock_step2.check_env.return_value = {}
        mock_step2.inputs = {"input1": {"stepId": "step1", "output": "output1"}}

        steps = {"step1": mock_step1, "step2": mock_step2}

        # Execute
        result_steps, result_graph = Orchestrator._load_from_json_content("test_file.json", steps)

        # Verify
        assert "step1" in result_steps
        assert "step2" in result_steps
        assert result_graph == mock_graph

    @patch("flowpipe.Graph")
    def test_load_from_json_content_with_missing_precedent(self, mock_graph_class):
        # Setup
        mock_graph = MagicMock()
        mock_graph_class.return_value = mock_graph

        # Create mock steps
        mock_step1 = MagicMock()
        mock_step1.id = "step1"
        mock_step1.precedents = ["non_existent_step"]
        mock_step1.check_env.return_value = {}

        steps = {"step1": mock_step1}

        # Execute and verify
        with pytest.raises(ValueError):
            Orchestrator._load_from_json_content("test_file.json", steps)

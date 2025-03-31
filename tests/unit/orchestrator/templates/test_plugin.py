import pytest
from unittest.mock import MagicMock, patch, mock_open
import json
import pathlib

from cosmotech.orchestrator.templates.plugin import Plugin
from cosmotech.orchestrator.core.command_template import CommandTemplate


class TestPlugin:
    def test_init_sets_name_from_file_path(self):
        # Setup
        file_path = "/path/to/plugin/file.py"

        # Execute
        plugin = Plugin(file_path)

        # Verify
        assert plugin.name == "plugin"
        assert plugin.templates == {}
        assert plugin.exit_commands == []

    def test_register_template_creates_and_registers_template(self):
        # Setup
        plugin = Plugin("/path/to/plugin.py")
        template_dict = {"id": "test-template", "command": "echo", "description": "Test template"}

        # Execute
        result = plugin.register_template(template_dict)

        # Verify
        assert isinstance(result, CommandTemplate)
        assert result.id == "test-template"
        assert result.command == "echo"
        assert result.description == "Test template"
        assert result.sourcePlugin == "to"  # The name is derived from the parent directory name of the file path
        assert "test-template" in plugin.templates
        assert plugin.templates["test-template"] == result

    def test_register_template_returns_false_for_invalid_template(self):
        # Setup
        plugin = Plugin("/path/to/plugin.py")
        # Missing required 'id' field
        template_dict = {"command": "echo"}

        # Execute and Verify
        # The current implementation raises a TypeError, so we need to catch it
        # and verify that no templates were registered
        result = plugin.register_template(template_dict)
        # If we get here, the test should fail
        assert result == False

    @patch("pathlib.Path.glob")
    @patch("pathlib.Path.is_file")
    @patch("json.load")
    @patch("cosmotech.orchestrator.templates.plugin.CommandTemplate")
    def test_load_folder_loads_templates_from_json_files(
        self, mock_command_template, mock_json_load, mock_is_file, mock_glob
    ):
        # Setup
        plugin = Plugin("/path/to/plugin.py")

        # Mock glob to return template files
        mock_path1 = MagicMock()
        mock_path1.is_file.return_value = True
        mock_path1.__str__.return_value = "/path/to/templates/template1.json"
        mock_path1.open = mock_open(read_data="{}")

        mock_path2 = MagicMock()
        mock_path2.is_file.return_value = True
        mock_path2.__str__.return_value = "/path/to/templates/template2.json"
        mock_path2.open = mock_open(read_data="{}")

        mock_glob.return_value = [mock_path1, mock_path2]

        # Mock is_file to return True for all paths
        mock_is_file.return_value = True

        # Mock json.load to return template definitions
        mock_json_load.side_effect = [
            {"commandTemplates": [{"id": "template1", "command": "echo"}, {"id": "template2", "command": "ls"}]},
            {"id": "template3", "command": "cat"},  # Single template
        ]

        # Mock CommandTemplate to return mock templates
        mock_template1 = MagicMock()
        mock_template1.id = "template1"
        mock_template2 = MagicMock()
        mock_template2.id = "template2"
        mock_template3 = MagicMock()
        mock_template3.id = "template3"

        mock_command_template.side_effect = [mock_template1, mock_template2, mock_template3]

        # Execute
        result = plugin.load_folder(pathlib.Path("/path/to/plugin"))

        # Verify
        assert result == 3  # 3 templates loaded
        assert mock_glob.called
        assert mock_json_load.call_count == 2
        assert mock_command_template.call_count == 3

    @patch("pathlib.Path.glob")
    @patch("pathlib.Path.is_file")
    @patch("json.load")
    @patch("cosmotech.orchestrator.templates.plugin.CommandTemplate")
    def test_load_folder_handles_exit_commands(self, mock_command_template, mock_json_load, mock_is_file, mock_glob):
        # Setup
        plugin = Plugin("/path/to/plugin.py")

        # Mock glob to return template files including exit handler
        mock_path1 = MagicMock()
        mock_path1.is_file.return_value = True
        mock_path1.__str__.return_value = "/path/to/templates/template1.json"
        mock_path1.open = mock_open(read_data="{}")

        mock_path2 = MagicMock()
        mock_path2.is_file.return_value = True
        mock_path2.__str__.return_value = "/path/to/templates/on_exit/exit_handler.json"
        mock_path2.open = mock_open(read_data="{}")

        mock_glob.return_value = [mock_path1, mock_path2]

        # Mock is_file to return True for all paths
        mock_is_file.return_value = True

        # Mock json.load to return template definitions
        mock_json_load.side_effect = [
            {"id": "template1", "command": "echo"},
            {"id": "exit_handler", "command": "cleanup"},
        ]

        # Mock CommandTemplate to return mock templates
        mock_template1 = MagicMock()
        mock_template1.id = "template1"
        mock_exit_handler = MagicMock()
        mock_exit_handler.id = "exit_handler"

        mock_command_template.side_effect = [mock_template1, mock_exit_handler]

        # Mock __register_exit_command
        plugin._Plugin__register_exit_command = MagicMock()

        # Execute
        result = plugin.load_folder(pathlib.Path("/path/to/plugin"))

        # Verify
        assert result == 2  # 2 templates loaded
        assert mock_command_template.call_count == 2
        assert plugin._Plugin__register_exit_command.called
        assert plugin._Plugin__register_exit_command.call_args[0][0] == "exit_handler"

    @patch("pathlib.Path.glob")
    @patch("pathlib.Path.is_file")
    @patch("json.load")
    def test_load_folder_handles_json_decode_error(self, mock_json_load, mock_is_file, mock_glob):
        # Setup
        plugin = Plugin("/path/to/plugin.py")

        # Mock glob to return template files
        mock_path = MagicMock()
        mock_path.is_file.return_value = True
        mock_path.__str__.return_value = "/path/to/templates/invalid.json"
        # Create a mock for open that will be used by _path.open()
        mock_file = mock_open(read_data="{}")
        mock_path.open = mock_file

        mock_glob.return_value = [mock_path]

        # Mock is_file to return True
        mock_is_file.return_value = True

        # Mock json.load to raise JSONDecodeError
        mock_json_load.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)

        # Execute
        result = plugin.load_folder(pathlib.Path("/path/to/plugin"))

        # Verify
        assert result == 0  # No templates loaded
        assert mock_glob.called
        assert mock_json_load.called

    @patch("pathlib.Path.glob")
    @patch("pathlib.Path.is_file")
    @patch("json.load")
    def test_load_folder_handles_non_dict_json(self, mock_json_load, mock_is_file, mock_glob):
        # Setup
        plugin = Plugin("/path/to/plugin.py")

        # Mock glob to return template files
        mock_path = MagicMock()
        mock_path.is_file.return_value = True
        mock_path.__str__.return_value = "/path/to/templates/invalid.json"
        mock_path.open = mock_open(read_data="{}")

        mock_glob.return_value = [mock_path]

        # Mock is_file to return True
        mock_is_file.return_value = True

        # Mock json.load to return non-dict value
        mock_json_load.return_value = ["not a dict"]

        # Execute
        result = plugin.load_folder(pathlib.Path("/path/to/plugin"))

        # Verify
        assert result == 0  # No templates loaded
        assert mock_glob.called
        assert mock_json_load.called

    def test_register_template_and_exit_command(self):
        # Setup
        plugin = Plugin("/path/to/plugin.py")

        # Execute
        plugin._Plugin__register_template("exit_template", CommandTemplate(id="exit_template", command="cleanup"))
        plugin._Plugin__register_exit_command("exit_template")

        # Verify
        assert "exit_template" in plugin.templates
        assert "exit_template" in plugin.exit_commands

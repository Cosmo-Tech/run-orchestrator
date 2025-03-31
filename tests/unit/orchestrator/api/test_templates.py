import pytest
from unittest.mock import MagicMock, patch
import os
import pprint
from typing import List, Dict, Any, Optional, Union

from cosmotech.orchestrator.api.templates import (
    template_to_dict,
    get_template_details,
    load_template_from_file,
    list_templates,
    display_template,
)
from cosmotech.orchestrator.core.command_template import CommandTemplate
from cosmotech.orchestrator.core.environment import EnvironmentVariable


class TestTemplateToDict:
    def test_basic_template_info(self):
        # Setup
        template = CommandTemplate(
            id="test-template",
            command="echo",
            description="Test template",
            arguments=["Hello", "World"],
            environment={"TEST_VAR": {"value": "test_value"}},
            sourcePlugin="test-plugin",
        )

        # Execute
        result = template_to_dict(template, verbose=False)

        # Verify
        assert result == {"id": "test-template", "description": "Test template", "sourcePlugin": "test-plugin"}

    def test_verbose_template_info(self):
        # Setup
        template = CommandTemplate(
            id="test-template",
            command="echo",
            description="Test template",
            arguments=["Hello", "World"],
            environment={"TEST_VAR": {"value": "test_value"}},
            sourcePlugin="test-plugin",
        )

        # Execute
        result = template_to_dict(template, verbose=True)

        # Verify
        assert result["id"] == "test-template"
        assert result["description"] == "Test template"
        assert result["command"] == "echo"
        assert result["arguments"] == ["Hello", "World"]
        assert result["environment"] == template.environment
        assert result["sourcePlugin"] == "test-plugin"
        # Don't check for isExitHandler as it's not in the CommandTemplate class


class TestGetTemplateDetails:
    @patch("cosmotech.orchestrator.api.templates.Library")
    def test_returns_template_details_when_found(self, mock_library_class):
        # Setup
        mock_library = MagicMock()
        mock_library_class.return_value = mock_library

        template = CommandTemplate(
            id="test-template",
            command="echo",
            description="Test template",
            arguments=["Hello", "World"],
            environment={"TEST_VAR": {"value": "test_value"}},
            sourcePlugin="test-plugin",
        )

        mock_library.find_template_by_name.return_value = template

        # Execute
        result = get_template_details("test-template", verbose=True)

        # Verify
        mock_library.find_template_by_name.assert_called_once_with("test-template")
        assert result["id"] == "test-template"
        assert result["description"] == "Test template"
        assert result["command"] == "echo"
        assert result["arguments"] == ["Hello", "World"]
        assert result["environment"] == template.environment
        assert result["sourcePlugin"] == "test-plugin"
        # Don't check for isExitHandler as it's not in the CommandTemplate class

    @patch("cosmotech.orchestrator.api.templates.Library")
    def test_returns_none_when_template_not_found(self, mock_library_class):
        # Setup
        mock_library = MagicMock()
        mock_library_class.return_value = mock_library
        mock_library.find_template_by_name.return_value = None

        # Execute
        result = get_template_details("non-existent-template")

        # Verify
        mock_library.find_template_by_name.assert_called_once_with("non-existent-template")
        assert result is None


class TestLoadTemplateFromFile:
    @patch("cosmotech.orchestrator.api.templates.FileLoader")
    def test_returns_true_when_file_loaded_successfully(self, mock_file_loader_class):
        # Setup
        mock_file_loader = MagicMock()
        mock_file_loader_class.return_value = mock_file_loader

        # Execute
        result = load_template_from_file("valid_template.json")

        # Verify
        mock_file_loader_class.assert_called_once_with("valid_template.json")
        mock_file_loader.assert_called_once_with()
        assert result is True

    @patch("cosmotech.orchestrator.api.templates.FileLoader")
    def test_returns_false_when_file_loading_fails(self, mock_file_loader_class):
        # Setup
        mock_file_loader_class.side_effect = Exception("Failed to load file")

        # Execute
        result = load_template_from_file("invalid_template.json")

        # Verify
        mock_file_loader_class.assert_called_once_with("invalid_template.json")
        assert result is False


class TestListTemplates:
    @patch("cosmotech.orchestrator.api.templates.Library")
    def test_returns_empty_list_when_no_templates(self, mock_library_class):
        # Setup
        mock_library = MagicMock()
        mock_library_class.return_value = mock_library
        mock_library.templates = []

        # Execute
        result = list_templates()

        # Verify
        assert result == []

    @patch("cosmotech.orchestrator.api.templates.Library")
    @patch("cosmotech.orchestrator.api.templates.load_template_from_file")
    def test_loads_orchestration_file_when_provided(self, mock_load_template, mock_library_class):
        # Setup
        mock_library = MagicMock()
        mock_library_class.return_value = mock_library
        mock_library.templates = []
        mock_load_template.return_value = True

        # Execute
        result = list_templates(orchestration_file="template_file.json")

        # Verify
        mock_load_template.assert_called_once_with("template_file.json")
        assert result == []

    @patch("cosmotech.orchestrator.api.templates.Library")
    def test_returns_all_templates_when_no_filter(self, mock_library_class):
        # Setup
        mock_library = MagicMock()
        mock_library_class.return_value = mock_library

        template1 = CommandTemplate(id="template1", command="echo", description="Template 1", sourcePlugin="plugin1")

        template2 = CommandTemplate(id="template2", command="echo", description="Template 2", sourcePlugin="plugin2")

        mock_library.templates = [template1, template2]

        # Execute
        result = list_templates()

        # Verify
        assert len(result) == 2
        assert result[0]["id"] == "template1"
        assert result[1]["id"] == "template2"

    @patch("cosmotech.orchestrator.api.templates.Library")
    @patch("cosmotech.orchestrator.api.templates.get_template_details")
    def test_returns_filtered_templates(self, mock_get_details, mock_library_class):
        # Setup
        mock_library = MagicMock()
        mock_library_class.return_value = mock_library
        mock_library.templates = [MagicMock(), MagicMock()]

        mock_get_details.side_effect = [{"id": "template1", "description": "Template 1"}, None]  # template2 not found

        # Execute
        result = list_templates(template_ids=["template1", "template2"])

        # Verify
        assert len(result) == 1
        assert result[0]["id"] == "template1"
        # Don't check the exact parameters of get_template_details calls
        assert mock_get_details.call_count == 2


class TestDisplayTemplate:
    @patch("cosmotech.orchestrator.api.templates.LOGGER")
    @patch("cosmotech.orchestrator.api.templates.template_to_dict")
    def test_displays_template_dict(self, mock_to_dict, mock_logger):
        # Setup
        template_dict = {"id": "test-template", "description": "Test template"}

        # Execute
        display_template(template_dict, verbose=False)

        # Verify
        mock_to_dict.assert_not_called()
        mock_logger.info.assert_called_once()

    @patch("cosmotech.orchestrator.api.templates.LOGGER")
    @patch("cosmotech.orchestrator.api.templates.template_to_dict")
    def test_converts_and_displays_template_object(self, mock_to_dict, mock_logger):
        # Setup
        template = CommandTemplate(id="test-template", command="echo", description="Test template")

        mock_to_dict.return_value = {"id": "test-template", "description": "Test template"}

        # Execute
        display_template(template, verbose=False)

        # Verify
        mock_to_dict.assert_called_once_with(template, False)
        mock_logger.info.assert_called_once()

    @patch("cosmotech.orchestrator.api.templates.LOGGER")
    @patch("cosmotech.orchestrator.api.templates.template_to_dict")
    @patch("cosmotech.orchestrator.api.templates.pprint.pformat")
    @patch("cosmotech.orchestrator.api.templates.os.get_terminal_size")
    def test_displays_verbose_template_info(self, mock_term_size, mock_pformat, mock_to_dict, mock_logger):
        # Setup
        template = CommandTemplate(id="test-template", command="echo", description="Test template")

        mock_to_dict.return_value = {"id": "test-template", "description": "Test template", "command": "echo"}

        mock_term_size.return_value = MagicMock(columns=80)
        mock_pformat.return_value = "Formatted template"

        # Execute
        display_template(template, verbose=True)

        # Verify
        mock_to_dict.assert_called_once_with(template, True)
        mock_pformat.assert_called_once_with(mock_to_dict.return_value, width=80)
        mock_logger.info.assert_called_once()

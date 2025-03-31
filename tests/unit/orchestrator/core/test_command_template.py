import pytest
from unittest.mock import MagicMock, patch
from dataclasses import dataclass, field
from typing import Union

from cosmotech.orchestrator.core.command_template import CommandTemplate
from cosmotech.orchestrator.core.environment import EnvironmentVariable


class TestCommandTemplate:
    def test_post_init_converts_environment_dict_to_env_vars(self):
        # Setup
        env_dict = {
            "TEST_VAR1": {"value": "value1", "description": "Test var 1"},
            "TEST_VAR2": {"defaultValue": "default2", "description": "Test var 2"},
        }

        # Execute
        template = CommandTemplate(id="test-template", command="echo", environment=env_dict)

        # Verify
        assert isinstance(template.environment["TEST_VAR1"], EnvironmentVariable)
        assert isinstance(template.environment["TEST_VAR2"], EnvironmentVariable)
        assert template.environment["TEST_VAR1"].name == "TEST_VAR1"
        assert template.environment["TEST_VAR1"].value == "value1"
        assert template.environment["TEST_VAR1"].description == "Test var 1"
        assert template.environment["TEST_VAR2"].name == "TEST_VAR2"
        assert template.environment["TEST_VAR2"].defaultValue == "default2"
        assert template.environment["TEST_VAR2"].description == "Test var 2"

    def test_serialize_with_all_fields(self):
        # Setup
        template = CommandTemplate(
            id="test-template",
            command="echo",
            description="Test template",
            arguments=["Hello", "World"],
            environment={"TEST_VAR": {"value": "test_value", "description": "Test var"}},
            useSystemEnvironment=True,
            sourcePlugin="test-plugin",
        )

        # Execute
        result = template.serialize()

        # Verify
        assert result["id"] == "test-template"
        assert result["command"] == "echo"
        assert result["description"] == "Test template"
        assert result["arguments"] == ["Hello", "World"]
        assert "environment" in result
        assert "TEST_VAR" in result["environment"]
        assert result["useSystemEnvironment"] is True

    def test_serialize_with_minimal_fields(self):
        # Setup
        template = CommandTemplate(id="test-template", command="echo")

        # Execute
        result = template.serialize()

        # Verify
        assert result["id"] == "test-template"
        assert result["command"] == "echo"
        assert "description" not in result
        assert "arguments" not in result
        assert "environment" not in result
        assert "useSystemEnvironment" not in result

    def test_serialize_with_empty_collections(self):
        # Setup
        template = CommandTemplate(id="test-template", command="echo", arguments=[], environment={})

        # Execute
        result = template.serialize()

        # Verify
        assert result["id"] == "test-template"
        assert result["command"] == "echo"
        assert "arguments" not in result
        assert "environment" not in result

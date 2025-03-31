import pytest
from unittest.mock import MagicMock
import json

from cosmotech.orchestrator.utils.json import CustomJSONEncoder
from cosmotech.orchestrator.core.command_template import CommandTemplate
from cosmotech.orchestrator.core.environment import EnvironmentVariable
from cosmotech.orchestrator.core.step import Step


class TestCustomJSONEncoder:
    def test_encodes_command_template(self):
        # Setup
        encoder = CustomJSONEncoder()
        template = CommandTemplate(id="test-template", command="echo", description="Test template")

        # Execute
        result = encoder.default(template)

        # Verify
        assert result == template.serialize()

    def test_encodes_environment_variable(self):
        # Setup
        encoder = CustomJSONEncoder()
        env_var = EnvironmentVariable(name="TEST_VAR", value="test_value", description="Test variable")

        # Execute
        result = encoder.default(env_var)

        # Verify
        assert result == env_var.serialize()

    def test_encodes_step(self):
        # Setup
        encoder = CustomJSONEncoder()
        step = Step(id="test-step", command="echo", description="Test step")

        # Execute
        result = encoder.default(step)

        # Verify
        assert result == step.serialize()

    def test_raises_type_error_for_unknown_types(self):
        # Setup
        encoder = CustomJSONEncoder()
        unknown_obj = object()

        # Execute and verify
        with pytest.raises(TypeError):
            encoder.default(unknown_obj)

    def test_full_json_encoding(self):
        # Setup
        template = CommandTemplate(id="test-template", command="echo", description="Test template")

        # Execute
        result = json.dumps(template, cls=CustomJSONEncoder)

        # Verify
        expected = json.dumps(template.serialize())
        assert result == expected

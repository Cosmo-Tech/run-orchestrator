import pytest
from unittest.mock import MagicMock, patch
import os

from cosmotech.orchestrator.core.environment import EnvironmentVariable


class TestEnvironmentVariable:
    def test_is_required_returns_true_when_no_value_or_default(self):
        # Setup
        env_var = EnvironmentVariable(name="TEST_VAR", optional=False)

        # Execute and verify
        assert env_var.is_required() is True

    def test_is_required_returns_false_when_has_value(self):
        # Setup
        env_var = EnvironmentVariable(name="TEST_VAR", value="test_value", optional=False)

        # Execute and verify
        assert env_var.is_required() is False

    def test_is_required_returns_false_when_has_default_value(self):
        # Setup
        env_var = EnvironmentVariable(name="TEST_VAR", defaultValue="default_value", optional=False)

        # Execute and verify
        assert env_var.is_required() is False

    def test_is_required_returns_false_when_optional(self):
        # Setup
        env_var = EnvironmentVariable(name="TEST_VAR", optional=True)

        # Execute and verify
        assert env_var.is_required() is False

    @patch.dict(os.environ, {"TEST_VAR": "env_value"})
    def test_effective_value_returns_value_when_set(self):
        # Setup
        env_var = EnvironmentVariable(name="TEST_VAR", value="test_value", defaultValue="default_value")

        # Execute
        result = env_var.effective_value()

        # Verify
        assert result == "test_value"

    @patch.dict(os.environ, {"TEST_VAR": "env_value"})
    def test_effective_value_returns_env_var_when_no_value(self):
        # Setup
        env_var = EnvironmentVariable(name="TEST_VAR", defaultValue="default_value")

        # Execute
        result = env_var.effective_value()

        # Verify
        assert result == "env_value"

    @patch.dict(os.environ, {})
    def test_effective_value_returns_default_when_no_value_or_env_var(self):
        # Setup
        env_var = EnvironmentVariable(name="TEST_VAR", defaultValue="default_value")

        # Execute
        result = env_var.effective_value()

        # Verify
        assert result == "default_value"

    @patch.dict(os.environ, {})
    def test_effective_value_returns_none_when_no_value_default_or_env_var(self):
        # Setup
        env_var = EnvironmentVariable(name="TEST_VAR")

        # Execute
        result = env_var.effective_value()

        # Verify
        assert result is None

    def test_join_combines_values_from_other_env_var(self):
        # Setup
        env_var1 = EnvironmentVariable(name="TEST_VAR", description="Original description")

        env_var2 = EnvironmentVariable(
            name="TEST_VAR",
            value="test_value",
            defaultValue="default_value",
            description="New description",
            optional=True,
        )

        # Execute
        env_var1.join(env_var2)

        # Verify
        assert env_var1.value == "test_value"
        assert env_var1.defaultValue == "default_value"
        assert env_var1.description == "Original description"  # Original description is preserved
        assert env_var1.optional is True

    def test_join_preserves_original_values_when_other_has_none(self):
        # Setup
        env_var1 = EnvironmentVariable(
            name="TEST_VAR",
            value="original_value",
            defaultValue="original_default",
            description="Original description",
            optional=False,
        )

        env_var2 = EnvironmentVariable(name="TEST_VAR")

        # Execute
        env_var1.join(env_var2)

        # Verify
        assert env_var1.value == "original_value"
        assert env_var1.defaultValue == "original_default"
        assert env_var1.description == "Original description"
        assert env_var1.optional is False

    def test_serialize_with_all_fields(self):
        # Setup
        env_var = EnvironmentVariable(
            name="TEST_VAR",
            value="test_value",
            defaultValue="default_value",
            description="Test description",
            optional=True,
        )

        # Execute
        result = env_var.serialize()

        # Verify
        assert result["value"] == "test_value"
        assert result["defaultValue"] == "default_value"
        assert result["description"] == "Test description"
        assert result["optional"] is True

    def test_serialize_with_minimal_fields(self):
        # Setup
        env_var = EnvironmentVariable(name="TEST_VAR")

        # Execute
        result = env_var.serialize()

        # Verify
        assert result == {}

    def test_serialize_with_some_fields(self):
        # Setup
        env_var = EnvironmentVariable(name="TEST_VAR", description="Test description", optional=True)

        # Execute
        result = env_var.serialize()

        # Verify
        assert "value" not in result
        assert "defaultValue" not in result
        assert result["description"] == "Test description"
        assert result["optional"] is True

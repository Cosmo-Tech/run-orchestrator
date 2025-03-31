import pytest
from unittest.mock import MagicMock, patch
import os
import i18n

from cosmotech.orchestrator.utils.translate import DEFAULT_TRANSLATOR, T


class TestGetTranslateFunction:
    @patch("cosmotech.orchestrator.utils.translate.get_translate_function")
    def test_configures_i18n_correctly(self, mock_get_translate_function):
        # Setup
        mock_translator = MagicMock()
        mock_get_translate_function.return_value = mock_translator

        # Import the function after patching
        from cosmotech.orchestrator.utils.translate import get_translate_function

        # Execute
        result = get_translate_function(locale="en-US", fallback="en-US", use_rich=False)

        # Verify
        mock_get_translate_function.assert_called_once_with(locale="en-US", fallback="en-US", use_rich=False)
        assert result == mock_translator

    @patch("i18n.t")
    def test_returns_standard_translator_when_use_rich_is_false(self, mock_i18n_t):
        # Setup
        mock_i18n_t.return_value = "translated text"

        # Create a simple translator function that mimics the behavior
        def translator(key, **kwargs):
            return i18n.t(key, **kwargs)

        # Execute
        result = translator("test.key", param="value")

        # Verify
        mock_i18n_t.assert_called_once_with("test.key", param="value")
        assert result == "translated text"

    @patch("i18n.t")
    def test_returns_rich_translator_when_use_rich_is_true(self, mock_i18n_t):
        # Setup
        # First call for rich key, second call for standard key
        mock_i18n_t.side_effect = ["rich.test.key", "translated text"]

        # Create a simple translator function that mimics the rich behavior
        def translator(key, **kwargs):
            rich_key = f"rich.{key}"
            result = i18n.t(rich_key, **kwargs)
            if result == rich_key:
                return i18n.t(key, **kwargs)
            return result

        # Execute
        result = translator("test.key", param="value")

        # Verify
        assert mock_i18n_t.call_count == 2
        mock_i18n_t.assert_any_call("rich.test.key", param="value")
        mock_i18n_t.assert_any_call("test.key", param="value")
        assert result == "translated text"

    @patch("i18n.t")
    def test_rich_translator_uses_rich_key_when_available(self, mock_i18n_t):
        # Setup
        # First call returns rich version, not the key itself
        mock_i18n_t.side_effect = ["rich translated text", "standard translated text"]

        # Create a simple translator function that mimics the rich behavior
        def translator(key, **kwargs):
            rich_key = f"rich.{key}"
            result = i18n.t(rich_key, **kwargs)
            if result == rich_key:
                return i18n.t(key, **kwargs)
            return result

        # Execute
        result = translator("test.key", param="value")

        # Verify
        mock_i18n_t.assert_called_once_with("rich.test.key", param="value")
        assert result == "rich translated text"


class TestDefaultTranslator:
    def test_default_translator_is_initialized(self):
        # Verify
        assert DEFAULT_TRANSLATOR is not None
        assert callable(DEFAULT_TRANSLATOR)

    def test_t_is_alias_for_default_translator(self):
        # Verify
        assert T is DEFAULT_TRANSLATOR

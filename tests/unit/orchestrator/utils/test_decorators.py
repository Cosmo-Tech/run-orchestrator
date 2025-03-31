import pytest
from unittest.mock import MagicMock, patch
import os
import webbrowser

from cosmotech.orchestrator.utils.decorators import require_env, web_help
from cosmotech.orchestrator.utils.click import click


class TestRequireEnv:
    def test_function_runs_when_env_var_exists(self):
        # Setup
        @require_env("TEST_VAR", "Test variable")
        def test_function():
            return "success"

        with patch.dict(os.environ, {"TEST_VAR": "test_value"}):
            # Execute
            result = test_function()

            # Verify
            assert result == "success"

    def test_function_raises_error_when_env_var_missing(self):
        # Setup
        @require_env("MISSING_VAR", "Missing variable")
        def test_function():
            return "success"

        with patch.dict(os.environ, {}, clear=True):
            # Execute and verify
            with pytest.raises(EnvironmentError):
                test_function()

    def test_adds_documentation_to_function(self):
        # Setup
        @require_env("TEST_VAR", "Test variable")
        def test_function():
            """Original docstring."""
            return "success"

        # Verify
        assert "Original docstring." in test_function.__doc__
        assert "TEST_VAR" in test_function.__doc__
        assert "Test variable" in test_function.__doc__


class TestWebHelp:
    @patch("webbrowser.open")
    @patch("cosmotech.orchestrator.utils.decorators.LOGGER")
    def test_opens_documentation_url_when_flag_is_set(self, mock_logger, mock_webbrowser_open):
        # Setup
        mock_webbrowser_open.return_value = True

        # Mock the click context
        mock_ctx = MagicMock()

        # Create a callback function that we can test directly
        from cosmotech.orchestrator.utils.decorators import web_help

        callback = web_help("docs/test")(lambda: None).__click_params__[0].callback

        # Execute the callback directly
        callback(mock_ctx, None, True)  # ctx, param, value

        # Verify
        mock_webbrowser_open.assert_called_once()
        assert "docs/test" in mock_webbrowser_open.call_args[0][0]
        mock_logger.info.assert_called_once()
        mock_ctx.exit.assert_called_once_with(0)

    @patch("webbrowser.open")
    @patch("cosmotech.orchestrator.utils.decorators.LOGGER")
    def test_logs_warning_when_browser_fails_to_open(self, mock_logger, mock_webbrowser_open):
        # Setup
        mock_webbrowser_open.return_value = False

        # Mock the click context
        mock_ctx = MagicMock()

        # Create a callback function that we can test directly
        from cosmotech.orchestrator.utils.decorators import web_help

        callback = web_help("docs/test")(lambda: None).__click_params__[0].callback

        # Execute the callback directly
        callback(mock_ctx, None, True)  # ctx, param, value

        # Verify
        mock_webbrowser_open.assert_called_once()
        mock_logger.warning.assert_called_once()
        mock_ctx.exit.assert_called_once_with(0)

    def test_executes_function_when_flag_is_not_set(self):
        # Setup
        @web_help("docs/test")
        def test_command():
            return "command executed"

        # Execute
        result = test_command(web_help=False)

        # Verify
        assert result == "command executed"

    def test_adds_web_help_option_to_function(self):
        # Setup
        @web_help("docs/test")
        def test_command():
            return "command executed"

        # Verify
        # Check that the click.option decorator was applied
        assert hasattr(test_command, "__click_params__")

        # Find the web-help option
        web_help_param = None
        for param in test_command.__click_params__:
            if param.name == "web_help":
                web_help_param = param
                break

        assert web_help_param is not None
        assert web_help_param.is_flag
        assert web_help_param.help == "Open the web documentation"

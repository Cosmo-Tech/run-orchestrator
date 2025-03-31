import pytest
from unittest.mock import MagicMock, patch
import logging
import os
import sys
from rich.logging import RichHandler

from cosmotech.orchestrator.utils.logger import msg_split, log_data, get_logger, LOGGER


class TestMsgSplit:
    def test_splits_string_by_newlines(self):
        # Setup
        message = "Line 1\nLine 2\nLine 3"

        # Execute
        result = msg_split(message)

        # Verify
        assert result == ["Line 1", "Line 2", "Line 3"]

    def test_converts_non_string_to_string(self):
        # Setup
        message = 123

        # Execute
        result = msg_split(message)

        # Verify
        assert result == ["123"]


class TestCustomRichHandler:
    @patch.dict(os.environ, {"CSM_USE_RICH": "True"})
    def test_emit_splits_message_by_newlines(self):
        # We need to reload the logger module to apply the environment variable change
        import importlib
        import cosmotech.orchestrator.utils.logger

        importlib.reload(cosmotech.orchestrator.utils.logger)

        # Now we can import CustomRichHandler
        from cosmotech.orchestrator.utils.logger import CustomRichHandler

        # Mock the msg_split function to control its behavior
        with patch("cosmotech.orchestrator.utils.logger.msg_split") as mock_msg_split:
            # Setup
            mock_msg_split.return_value = ["Line 1", "Line 2"]

            # Also mock the parent class emit method
            with patch.object(RichHandler, "emit") as mock_super_emit:
                # Setup
                handler = CustomRichHandler()
                record = logging.LogRecord(
                    name="test_logger",
                    level=logging.INFO,
                    pathname="test_path",
                    lineno=1,
                    msg="Line 1\nLine 2",
                    args=(),
                    exc_info=None,
                )

                # Execute
                handler.emit(record)

                # Verify
                # Check that msg_split was called with the record's message
                mock_msg_split.assert_called_once_with("Line 1\nLine 2")

                # Check that emit was called twice (once for each line)
                assert mock_super_emit.call_count == 2

    @patch.dict(os.environ, {"CSM_USE_RICH": "True", "PAILLETTES": "True"})
    def test_formatter_with_paillettes(self):
        # We need to reload the logger module to apply the environment variable change
        import importlib
        import cosmotech.orchestrator.utils.logger

        importlib.reload(cosmotech.orchestrator.utils.logger)

        # Now we can check if the formatter has paillettes
        from cosmotech.orchestrator.utils.logger import FORMATTER

        # Verify that the format string contains paillettes
        assert "[bold yellow blink]***[/]" in FORMATTER._fmt


class TestCustomHandler:
    @patch.dict(os.environ, {"CSM_USE_RICH": "False"})
    def test_emit_splits_message_by_newlines(self):
        # We need to reload the logger module to apply the environment variable change
        import importlib
        import cosmotech.orchestrator.utils.logger

        importlib.reload(cosmotech.orchestrator.utils.logger)

        # Now we can import CustomHandler
        from cosmotech.orchestrator.utils.logger import CustomHandler

        # Mock the msg_split function to control its behavior
        with patch("cosmotech.orchestrator.utils.logger.msg_split") as mock_msg_split:
            # Setup
            mock_msg_split.return_value = ["Line 1", "Line 2"]

            # Also mock the parent class emit method
            with patch.object(logging.StreamHandler, "emit") as mock_super_emit:
                # Setup
                handler = CustomHandler()
                record = logging.LogRecord(
                    name="test_logger",
                    level=logging.INFO,
                    pathname="test_path",
                    lineno=1,
                    msg="Line 1\nLine 2",
                    args=(),
                    exc_info=None,
                )

                # Execute
                handler.emit(record)

                # Verify
                # Check that msg_split was called with the record's message
                mock_msg_split.assert_called_once_with("Line 1\nLine 2")

                # Check that emit was called twice (once for each line)
                assert mock_super_emit.call_count == 2


class TestLogData:
    @patch("cosmotech.orchestrator.utils.logger._data_logger")
    def test_logs_data_in_correct_format(self, mock_data_logger):
        # Setup
        name = "test_output"
        value = "test_value"

        # Execute
        log_data(name, value)

        # Verify
        mock_data_logger.info.assert_called_once_with("CSM-OUTPUT-DATA:test_output:test_value")


class TestGetLogger:
    @patch("logging.getLogger")
    def test_returns_logger_with_handler_and_level(self, mock_get_logger):
        # Setup
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        mock_logger.hasHandlers.return_value = False

        # Execute
        result = get_logger("test_logger", level=logging.DEBUG)

        # Verify
        mock_get_logger.assert_called_once_with("test_logger")
        mock_logger.addHandler.assert_called_once()
        mock_logger.setLevel.assert_called_once_with(logging.DEBUG)
        assert result == mock_logger

    @patch("logging.getLogger")
    def test_does_not_add_handler_if_already_has_handlers(self, mock_get_logger):
        # Setup
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        mock_logger.hasHandlers.return_value = True

        # Execute
        result = get_logger("test_logger")

        # Verify
        mock_get_logger.assert_called_once_with("test_logger")
        mock_logger.addHandler.assert_not_called()
        mock_logger.setLevel.assert_called_once()
        assert result == mock_logger


class TestLogger:
    def test_logger_is_initialized(self):
        # Verify
        assert LOGGER is not None
        assert isinstance(LOGGER, logging.Logger)
        assert LOGGER.name == "csm.run.orchestrator"

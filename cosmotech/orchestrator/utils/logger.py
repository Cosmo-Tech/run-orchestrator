# Copyright (C) - 2023 - 2025 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import logging
import os

import sys
from rich.highlighter import NullHighlighter
from rich.logging import RichHandler

_format = "%(message)s"


def msg_split(message):
    if not isinstance(message, str):
        message = str(message)
    return message.split("\n")


if os.environ.get("CSM_USE_RICH", "False").lower() in ("true", "1", "yes", "t", "y"):
    if "PAILLETTES" in os.environ:
        paillettes = "[bold yellow blink]***[/]"
        _format = f"{paillettes} {_format} {paillettes}"
    FORMATTER = logging.Formatter(
        fmt=_format,
        datefmt="[%Y/%m/%d-%H:%M:%S]",
    )
    HIGLIGHTER = NullHighlighter()

    class CustomRichHandler(RichHandler):
        def __init__(self, *args, **kwargs):
            super(CustomRichHandler, self).__init__(*args, **kwargs)

        def emit(self, record):
            messages = msg_split(record.msg)
            for message in messages:
                record.msg = message
                super(CustomRichHandler, self).emit(record)

    HANDLER = CustomRichHandler(
        rich_tracebacks=True, omit_repeated_times=False, show_path=False, markup=True, highlighter=HIGLIGHTER
    )
else:
    FORMATTER = logging.Formatter(fmt="{asctime} {levelname:<8} {message}", style="{", datefmt="[%Y/%m/%d-%H:%M:%S]")

    class CustomHandler(logging.StreamHandler):
        def __init__(self, *args, **kwargs):
            super(CustomHandler, self).__init__(*args, **kwargs)

        def emit(self, record):
            messages = msg_split(record.msg)
            for message in messages:
                record.msg = message
                super(CustomHandler, self).emit(record)

    HANDLER = CustomHandler(sys.stdout)

HANDLER.setFormatter(FORMATTER)

# Create a dedicated logger for data output with a simple formatter
_data_formatter = logging.Formatter(fmt="%(message)s")
_data_handler = logging.StreamHandler(sys.stdout)
_data_handler.setFormatter(_data_formatter)
_data_logger = logging.getLogger("csm.run.orchestrator.data")
_data_logger.addHandler(_data_handler)
_data_logger.setLevel(logging.INFO)
# Prevent the data logger from propagating to parent loggers
_data_logger.propagate = False


def log_data(name: str, value: str):
    """Log a value in the CSM-OUTPUT-DATA format for step-to-step transfer.

    Args:
        name: The name of the output variable
        value: The value to output
    """
    _data_logger.info(f"CSM-OUTPUT-DATA:{name}:{value}")


def get_logger(logger_name: str, level=logging.INFO) -> logging.Logger:
    _logger = logging.getLogger(logger_name)
    if not _logger.hasHandlers():
        _logger.addHandler(HANDLER)
    if isinstance(level, str):
        level = logging.getLevelNamesMapping().get(level.upper(), logging.INFO)
    _logger.setLevel(level)
    return _logger


LOGGER = get_logger("csm.run.orchestrator")

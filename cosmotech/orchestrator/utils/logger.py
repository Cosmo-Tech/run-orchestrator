# Copyright (C) - 2023 - 2024 - Cosmo Tech
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

if sys.__stdout__.isatty():
    if "PAILLETTES" in os.environ:
        paillettes = "[bold yellow blink]***[/]"
        _format = f"{paillettes} {_format} {paillettes}"
    FORMATTER = logging.Formatter(fmt=_format,
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


    HANDLER = CustomRichHandler(rich_tracebacks=True,
                                omit_repeated_times=False,
                                show_path=False,
                                markup=True,
                                highlighter=HIGLIGHTER)
else:
    FORMATTER = logging.Formatter(fmt="{asctime} {levelname:<8} {message}",
                                  style="{",
                                  datefmt="[%Y/%m/%d-%H:%M:%S]")


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


def get_logger(
    logger_name: str,
    level=logging.INFO
) -> logging.Logger:
    _logger = logging.getLogger(logger_name)
    if not _logger.hasHandlers():
        _logger.addHandler(HANDLER)
    _logger.setLevel(level)
    return _logger


LOGGER = get_logger("csm.run.orchestrator")

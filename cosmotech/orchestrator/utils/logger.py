from rich.logging import RichHandler
import logging
import os

LOGGER = logging.getLogger("csm.orchestrator")

_format = "%(message)s"

if "PAILLETTES" in os.environ:
    paillettes = "[bold yellow blink]***[/]"
    _format = f"{paillettes} {_format} {paillettes}"

logging.basicConfig(
    format=_format,
    datefmt="[%Y/%m/%d-%X]",
    handlers=[RichHandler(rich_tracebacks=True,
                          omit_repeated_times=False,
                          show_path=False,
                          markup=True)])
LOGGER.setLevel(logging.INFO)

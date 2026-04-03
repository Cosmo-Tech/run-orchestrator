# Copyright (C) - 2023 - 2025 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import subprocess
import signal
import sys

from cosmotech.csm_orc_api import STATIC_DIR, VISUAL_ORC_SRC_DIR, is_dev_mode
from cosmotech.orchestrator.utils.click import click
from cosmotech.orchestrator.utils.decorators import web_help
from cosmotech.orchestrator.utils.logger import LOGGER


@click.command()
@click.option(
    "--host",
    envvar="CSM_ORC_GUI_HOST",
    show_envvar=True,
    default="0.0.0.0",
    show_default=True,
    help="Host to bind the server to.",
)
@click.option(
    "--port",
    envvar="CSM_ORC_GUI_PORT",
    show_envvar=True,
    default=8080,
    show_default=True,
    type=int,
    help="Port to bind the server to.",
)
@click.option(
    "--dev/--no-dev",
    "dev_mode",
    default=None,
    help="Force dev mode (start Vite dev server alongside the API). Auto-detected if not specified.",
)
@web_help("commands/gui")
def gui_command(host: str, port: int, dev_mode: bool):
    """Start the Visual Orchestrator GUI.

    In release mode (built static files available), serves the web app from the packaged static files.
    In dev mode (editable install with sources), starts the Vite dev server alongside the API backend."""

    # Auto-detect dev mode if not explicitly set
    if dev_mode is None:
        dev_mode = is_dev_mode()

    if dev_mode:
        _start_dev_mode(host, port)
    else:
        if not (STATIC_DIR / "index.html").exists():
            LOGGER.error(
                "No built static files found and no visual_orchestrator source directory detected. "
                "Please build the web app first (scripts/build_webapp.sh) or use --dev mode with sources available."
            )
            raise click.Abort()
        _start_release_mode(host, port)


def _start_release_mode(host: str, port: int):
    """Start uvicorn serving the FastAPI app with built static files."""
    import uvicorn

    LOGGER.info(f"Starting Visual Orchestrator in release mode on http://{host}:{port}")
    LOGGER.info(f"Open your browser at http://localhost:{port}")
    uvicorn.run("cosmotech.csm_orc_api:app", host=host, port=port)


def _start_dev_mode(host: str, port: int):
    """Start uvicorn + Vite dev server for development."""
    import uvicorn

    if not (VISUAL_ORC_SRC_DIR / "package.json").exists():
        LOGGER.error(
            "Dev mode requested but visual_orchestrator source directory not found. "
            "Make sure you have an editable install (pip install -e .)."
        )
        raise click.Abort()

    # Check if node_modules exists, if not run npm install
    node_modules = VISUAL_ORC_SRC_DIR / "node_modules"
    if not node_modules.exists():
        LOGGER.info("Installing npm dependencies for visual_orchestrator...")
        subprocess.run(
            ["npm", "install"],
            cwd=str(VISUAL_ORC_SRC_DIR),
            check=True,
        )

    LOGGER.info(f"Starting Visual Orchestrator in dev mode")
    LOGGER.info(f"API server on http://{host}:{port}")
    LOGGER.info(f"Vite dev server will start on http://localhost:5173")
    LOGGER.info(f"Open your browser at http://localhost:5173")

    # Start Vite dev server as a subprocess
    vite_process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=str(VISUAL_ORC_SRC_DIR),
    )

    def cleanup(signum=None, frame=None):
        LOGGER.info("Shutting down Vite dev server...")
        vite_process.terminate()
        try:
            vite_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            vite_process.kill()
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    try:
        uvicorn.run("cosmotech.csm_orc_api:app", host=host, port=port, reload=True)
    finally:
        cleanup()

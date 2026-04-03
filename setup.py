"""
Custom setup.py that builds the frontend static files before packaging.

The frontend (cosmotech/visual_orchestrator) is a Vite + React app that
builds into cosmotech/csm_orc_api/static/. This setup.py hooks into the
setuptools build process to run 'npm ci && npm run build' automatically.
"""

import os
import subprocess
import sys
from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py
from setuptools.command.sdist import sdist


FRONTEND_DIR = Path(__file__).parent / "cosmotech" / "visual_orchestrator"
STATIC_DIR = Path(__file__).parent / "cosmotech" / "csm_orc_api" / "static"


def build_frontend():
    """Run npm ci && npm run build in the frontend directory."""
    if not FRONTEND_DIR.exists():
        print(f"[setup.py] Frontend directory not found: {FRONTEND_DIR}", file=sys.stderr)
        return

    # Check if npm is available
    try:
        subprocess.run(["npm", "--version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        if STATIC_DIR.exists() and any(STATIC_DIR.iterdir()):
            print("[setup.py] npm not found but static files already exist, skipping frontend build")
            return
        print(
            "[setup.py] WARNING: npm is not available and no pre-built static files found. "
            "The GUI will not work. Install Node.js/npm to build the frontend.",
            file=sys.stderr,
        )
        return

    print(f"[setup.py] Building frontend in {FRONTEND_DIR}")

    # Install dependencies
    subprocess.run(
        ["npm", "ci", "--ignore-scripts"],
        cwd=FRONTEND_DIR,
        check=True,
    )

    # Build the frontend (output goes to cosmotech/csm_orc_api/static/)
    subprocess.run(
        ["npm", "run", "build"],
        cwd=FRONTEND_DIR,
        check=True,
    )

    if STATIC_DIR.exists() and any(STATIC_DIR.iterdir()):
        print(f"[setup.py] Frontend built successfully -> {STATIC_DIR}")
    else:
        print(f"[setup.py] WARNING: Build completed but {STATIC_DIR} is empty", file=sys.stderr)


class BuildPyWithFrontend(build_py):
    """Custom build_py that builds the frontend first."""

    def run(self):
        build_frontend()
        super().run()


class SdistWithFrontend(sdist):
    """Custom sdist that builds the frontend first so static files are included."""

    def run(self):
        build_frontend()
        super().run()


setup(
    cmdclass={
        "build_py": BuildPyWithFrontend,
        "sdist": SdistWithFrontend,
    },
)

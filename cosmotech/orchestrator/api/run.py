# Copyright (C) - 2023 - 2025 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

"""
API functions for running templates.

This module provides functions that implement the core functionality of the
csm-orc run command, allowing them to be used directly without the CLI context.
"""

import pathlib
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from cosmotech.orchestrator import VERSION
from cosmotech.orchestrator.core.orchestrator import Orchestrator
from cosmotech.orchestrator.core.step import Step, StepStatus
from cosmotech.orchestrator.utils.logger import LOGGER
from cosmotech.orchestrator.utils.translate import T


def validate_template(template_path: str) -> bool:
    """
    Validate a template file without running it.

    Args:
        template_path: Path to the template file

    Returns:
        True if the template is valid, False otherwise
    """
    try:
        f = Orchestrator()
        f.load_json_file(template_path, validate_only=True)
        LOGGER.info(T("csm-orc.orchestrator.core.orchestrator.valid_file").format(file_path=template_path))
        return True
    except ValueError as e:
        LOGGER.error(e)
        return False


def display_environment(template_path: str) -> Dict[str, List[str]]:
    """
    Display environment variables required by a template.

    Args:
        template_path: Path to the template file

    Returns:
        Dictionary of environment variable names and their descriptions
    """
    f = Orchestrator()
    try:
        f.load_json_file(template_path, display_env=True)
        return {}  # The function above logs the environment variables
    except ValueError as e:
        LOGGER.error(e)
        raise ValueError(str(e))


def generate_env_file(template_path: str, target_path: str) -> bool:
    """
    Generate a .env file with all environment variables required by a template.

    Args:
        template_path: Path to the template file
        target_path: Path to write the .env file to

    Returns:
        True if the file was generated successfully, False otherwise
    """
    f = Orchestrator()
    try:
        s, g = f.load_json_file(template_path, display_env=True)
        LOGGER.info(T("csm-orc.cli.run.writing_env").format(target=target_path))
        _fp = pathlib.Path(target_path)
        _fp.parent.mkdir(parents=True, exist_ok=True)

        with _fp.open("w") as _f:
            _env: Dict[str, str] = dict()
            _env.update(
                {
                    k: v.description if v.effective_value() is None else v.effective_value()
                    for _s, _ in s.values()
                    for k, v in _s.environment.items()
                }
            )
            _f.writelines(f"{k}={v}\n" for k, v in sorted(_env.items(), key=lambda e: e[0]))
        return True
    except ValueError as e:
        LOGGER.error(e)
        return False


def run_template(
    template_path: str,
    dry_run: bool = False,
    display_env: bool = False,
    skipped_steps: List[str] = None,
    exit_handlers: bool = True,
) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Run a template file.

    Args:
        template_path: Path to the template file
        dry_run: Whether to run in dry-run mode
        display_env: Whether to display environment variables
        skipped_steps: List of steps to skip
        exit_handlers: Whether to run exit handlers

    Returns:
        Tuple of (success, results)
    """
    if skipped_steps is None:
        skipped_steps = []

    LOGGER.info(T("csm-orc.cli.run.starting").format(version=VERSION))
    f = Orchestrator()
    try:
        s, g = f.load_json_file(template_path, dry_run, display_env, skipped_steps)
    except ValueError as e:
        LOGGER.error(e)
        return False, None
    else:
        if g is None:
            return True, None

        success = True
        results = {}

        LOGGER.info(T("csm-orc.cli.run.sections.run"))
        g.evaluate(mode="threading")
        LOGGER.info(T("csm-orc.cli.run.sections.results"))

        for k, v in s.items():
            LOGGER.info(v[0].simple_repr())
            LOGGER.debug(str(v[0]))
            results[k] = v[0]
            if v[0].status == StepStatus.ERROR:
                success = False

        if exit_handlers:
            from cosmotech.orchestrator.templates.library import Library

            library = Library()
            exit_steps = []
            for command_template in library.list_exit_commands():
                _s = Step(
                    id=command_template,
                    commandId=command_template,
                    environment={"CSM_ORC_IS_SUCCESS": {"value": str(success)}},
                )
                _s.run(as_exit=True)
                exit_steps.append(_s)

            if exit_steps:
                LOGGER.info(T("csm-orc.cli.run.sections.exit_handlers"))

            for _s in exit_steps:
                LOGGER.info(_s.simple_repr())
                results[_s.id] = _s

        return success, results

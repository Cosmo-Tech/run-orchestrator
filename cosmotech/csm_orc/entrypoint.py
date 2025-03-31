# Copyright (C) - 2023 - 2025 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import subprocess

from cosmotech.orchestrator.api.entrypoint import run_entrypoint, EntrypointException
from cosmotech.orchestrator.utils.click import click


@click.command(hidden="True", context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
def entrypoint_command():
    """Docker entrypoint

    This command is used in CosmoTech docker containers only"""
    try:
        exit_code = run_entrypoint()
        if exit_code != 0:
            raise click.Abort()
    except EntrypointException as e:
        raise click.Abort()
    except subprocess.CalledProcessError:
        raise click.Abort()


if __name__ == "__main__":
    entrypoint_command()

# Copyright (C) - 2023 - 2023 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from setuptools import find_namespace_packages
from setuptools import setup

from cosmotech.orchestrator import VERSION

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='cosmotech-run-orchestrator',
    version=VERSION,
    author='Alexis Fossart',
    author_email='alexis.fossart@cosmotech.com',
    url="https://github.com/Cosmo-Tech/run-orchestrator",
    description='Orchestration suite for Cosmotech Run Templates',
    packages=find_namespace_packages(include=["cosmotech.*"]),
    include_package_data=True,
    zip_safe=False,
    long_description=long_description,
    long_description_content_type="text/markdown",
    license_files=("LICENSE",),
    install_requires=required,
    entry_points={
        'console_scripts': [
            'csm-orc=cosmotech.orchestrator.console_scripts.main:main',
        ]
    },
)

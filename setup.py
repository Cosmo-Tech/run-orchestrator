from setuptools import setup, find_namespace_packages
from cosmotech.orchestrator import VERSION

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='cosmotech-run-orchestrator',
    version=VERSION,
    author='Alexis Fossart',
    author_email='alexis.fossart@cosmotech.com',
    url="https://github.com/Cosmo-Tech/Babylon",
    description='Orchestration suite for Cosmotech Run Templates',
    packages=find_namespace_packages(include=["cosmotech.*"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=required,
    entry_points={
        'console_scripts': [
            'csm-run-orchestrator=cosmotech.orchestrator.console_scripts.main:main',
        ]
    },
)

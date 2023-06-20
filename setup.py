from setuptools import setup, find_namespace_packages
from cosmotech.orchestrator import VERSION

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='Run Template Orchestrator',
    version=VERSION,
    author='Alexis Fossart',
    author_email='alexis.fossart@cosmotech.com',
    url="https://github.com/Cosmo-Tech/Babylon",
    description='Simple orchestrator for Cosmotech Solutions',
    packages=find_namespace_packages(include=["cosmotech.*"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=required,
    entry_points={
        'console_scripts': [
            'cosmotech_scenario_downloader=cosmotech.orchestrator.console_scripts.scenario_data_downloader:main',
            'cosmotech_simulation_to_adx_connector=cosmotech.orchestrator.console_scripts.adx_scenario_connector:main',
            'cosmotech_run_step=cosmotech.orchestrator.console_scripts.run_step:main'
        ]
    },
)

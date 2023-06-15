
from setuptools import setup, find_packages
from run_template_orchestrator import VERSION

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='Run Template Orchestrator',
    version=VERSION,
    author='Alexis Fossart',
    author_email='alexis.fossart@cosmotech.com',
    url="https://github.com/Cosmo-Tech/Babylon",
    description='Simple orchestrator for Cosmotech Solutions',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=required,
    entry_points={
        'console_scripts': [
            'cosmotech_scenario_downloader=run_template_orchestrator.console_scripts.scenario_data_downloader:main'
        ]
    },
)
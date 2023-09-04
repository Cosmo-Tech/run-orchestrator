# Run Template Orchestrator ![%%VERSION%%](https://img.shields.io/badge/%%VERSION%%-2e303e?style=for-the-badge)

This repository contains the new Run Template Orchestrator used in the latest Cosmotech Solutions

## Installation

You need to add the orchestrator to the environment you want to use it on.

The following guide will suppose you have a CosmoTech Project called `MyProject` which is in the folder `~/MyProject`

It will also suppose you have a build version of the CosmoTech SDK in the folder `~/Cosmotech/Studio`

!!! info "Create a virtual environment and add dependencies (in bash)"
    ```bash
    # First move to your project folder
    cd ~/MyProject
    # Next create and activate a venv (here .venv)
    python -m venv .venv
    source .venv/bin/activate
    # Update your python path with the bindings from the sdk
    export PYTHONPATH=$PYTHONPATH:~/Cosmotech/Studio/lib/python/site-packages
    # Add the local wrappers for your solution to the python path
    export PYTHONPATH=$PYTHONPATH:~/MyProject/Generated/Build/Wrapping:~/MyProject/Generated/Build/Lib
    # Finally install the dependencies for your project (they should be in code/requirements.txt)
    pip install -r code/requirements.txt
    ``` 
    ??? note
        If you use the Cosmotech CLI `csmcli` you can replace the use of the `PYTHONPATH` environment variable by calls to `csm exec`

After all those commands you environment should be ready for a test, but first let's install the repository

=== "Install from sources"
    !!! info "Install the orchestrator from git sources"
        ```bash
        pip install git+ssh://git@github.com/Cosmo-Tech/run-orchestrator.git
        ```
    
    !!! info "Install the orchestrator from local sources"
        ```bash
        git clone ssh://git@github.com/Cosmo-Tech/run-orchestrator.git
        pip install ./run-orchestrator
        ```

=== "Install using Pypi"
    !!! info "Install using pip"
        ```bash
        pip install cosmotech-run-orchestrator
        ```

After installation a few commands are made available, documentation for each is available on the [commands documentation page](./commands/index.md)

!!! info "Autocompletion"
    Run the following command
    ```bash
    _CSM_ORC_COMPLETE=bash_source csm-orc > ~/.csm-orc-complete.bash
    ```
    then add the following line at the end of your `.bashrc` file
    ```bash
    . ~/.csm-orc-complete.bash
    ```
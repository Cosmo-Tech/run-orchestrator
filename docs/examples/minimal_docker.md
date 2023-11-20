---
description: Minimal project for a docker image compatible with the Cosmo Tech API
---

# Minimal docker project

## Description

This example will show you a minimal project that will allow you to build a `docker` image that will be able to run your orchestration files.

## Project description

```title="Project tree"
minimal_docker_project
├── code/
│   ├── main.py
│   └── run_templates/
│       └── RUN/
│           └── run.json
├── Dockerfile
└── requirements.txt
```

## File content

```python title="code/main.py" linenums="1"
--8<-- "examples/minimal_docker/code/main.py"
```

This python file will be run by using a simple orchestration file.

```json title="code/run_templates/RUN/run.json" linenums="1"
--8<-- "examples/minimal_docker/code/run_templates/RUN/run.json"
```

Now we only need to add our requirements for the project:

```requirements.txt title="requirements.txt"
--8<-- "examples/minimal_docker/requirements.txt"
```

And to finish a simple Dockerfile to build our docker image:

```dockerfile title="Dockerfile"
--8<-- "examples/minimal_docker/Dockerfile"
```

## Build the image

The image can be simply built using the following command:

```bash title="Build the docker image"
docker build . -t minimal_docker_orchestrator
```

## Run the image

The image can then be run using the following command:

```bash title="Run the docker image"
docker run example_orc
```

## Possible environment variables with the Cosmo Tech API

The Cosmo Tech API can send the following list of environment variable to your docker image which will be 
available for any orchestration file you may want to run in it

??? notes "List of environment variables"
    {{ read_yaml('partials/tutorial/advanced_cosmotech_simulator/api_envvars.yaml') }}
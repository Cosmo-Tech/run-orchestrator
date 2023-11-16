---
description: Simple tutorial to convert a fully local Simulator to a cloud ready docker image
---
# Make a Cosmo Tech Simulator cloud-ready

In this tutorial we will take our updated Brewery Simulator project as we left it in the [previous tutorial](./cosmotech_simulator.md)
and add modification to get it ready to be used inside a Cosmo Tech Platform.

!!! warning "Requirements"
    - `docker`
    - A Cosmo Tech Platform minimal version of 3.0
    - A Cosmo Tech SDK minimal version of 10.0
    - Installed SDK package must include `csmcli`

## How does the Cosmo Tech Platform runs orchestration?

The Cosmo Tech Platform will run pre-registered `docker` images based on the definition of `Solutions` in its API.

In the API you can define a `Solution` that will refer to a specific version of a `docker` image in a given repository.
That `Solution` defines sets of `Parameters` and `Run Templates`. 
Then `Workspaces` are defined in the API and point to a given `Solution` 
allowing you to create a `Scenario` which will tie together `Datasets`, `Parameters`, 
and a `Run Template` which will then be run by the API.

`Datasets` are a description of how and where data are stored, `Parameters` can be simple types 
or full `Datasets` allowing you to update the main `Dataset` of your `Scenario`, therefore
changing its initial state or behavior (or both).

Running your `Scenario` will create a `ScenarioRun` into the API 
and that `ScenarioRun` will make use of the `docker` image your previously defined.
The API will call the image with an `Entrypoint` called `entrypoint.py` and that call should be your full orchestration.

??? question "Why `entrypoint.py` and not `csm-orc` ?"
    The definition of the `Entrypoint` being `entrypoint.py` 
    is left for compatibility with old images on the Cosmo Tech API (pre 3.0).
    It will be changed in the future, but for now `csm-orc` comes bundled with 
    a script called `entrypoint.py` that allows both legacy and new runs of
    the `docker` image.

## How does `entrypoint.py` works?

The `entrypoint.py` command (and its equivalent `csm-orc entrypoint`) works using some Environment variables to switch between 3 modes:

- The general entrypoint with no special configuration that allow to run your `run templates` requiring the environment variable `CSM_RUN_TEMPLATE_ID` to be set with your run template name.
- The legacy entrypoint activated by setting the environment variable `CSM_ENTRYPOINT_LEGACY` to `true` which is made available for compatibility with pre 3.0 Cosmo Tech API.
- The direct simulator mode which requires the environment variable `CSM_RUN_TEMPLATE_ID` to not be set, and will then run the simulator by passing it any argument of the command.

Every `Environment Variable` passed to the command will be forwarded to the
`csm-orc run` command inside, and the command will be run with the working directory set to `/pkg/share`.

## Which `Environment Variables` are made available by the API?

The Cosmo Tech API will forward a set of environment variables to any Simulator containers. You can find the full list in the following table.

??? notes "List of environment variables"
    {{ read_yaml('partials/tutorial/advanced_cosmotech_simulator/api_envvars.yaml') }}

## Connect to the API to get our `Scenario` data

Multiple ways exists to connect to the API and query some data, but for simplicity there exists a command in `csm-orc` that will make use of known API environment variables and do the work for you.

That command is `csm-orc fetch-scenariorun-data` (documentation of the command is available [here](../commands/scenario_data_downloader.md)).

The command makes use of 5 environment variables set by the API (as described in the previous section):

- `CSM_ORGANIZATION_ID`
- `CSM_WORKSPACE_ID`
- `CSM_SCENARIO_ID`
- `CSM_DATASET_ABSOLUTE_PATH`
- `CSM_PARAMETERS_ABSOLUTE_PATH`

And uses 3 control environment variables:

- `WRITE_JSON`: If set to `true` will write a `parameters.json` file in `CSM_PARAMETERS_ABSOLUTE_PATH`.
- `WRITE_CSV`: If set to `true` will write a `parameters.csv` file in `CSM_PARAMETERS_ABSOLUTE_PATH`.
- `FETCH_DATASET`: If set to `true` will download all the `Datasets` tied to your scenario, 
     will write the main ones (not defined as a `Parameter`) in `CSM_DATASET_ABSOLUTE_PATH` 
     and will write the others in `CSM_PARAMETERS_ABSOLUTE_PATH/[parameter name]` 
     where `[parameter name]` is the name of the `Parameter` targeting the `Dataset` (with a type set to `%DATASETID%`).

With that command one can easily download any dataset defined in the Cosmo Tech API, 
as long as those datasets use one of the standard connections defined in the API 
(as of version 3.0: `Azure Blob Storage`, `Azure Digital Twin`, `TwinGraph Storage`).

## Combine everything in a `Run Template`

Using all those new information we can see that most of the actions needed to run our code based on API data are already prepackaged.

We can:

- Download our scenario information using `csm-orc fetch-scenariorun-data`.
- Apply our parameters with our `apply_parameters.py`.
- Run our simulation using `csm-orc run-step`.
- And send our simulation results to an external system (here Azure Data Explorer) by setting environment variables during the `run-step`.

It is then easy to update our previous `run.json` to take those changes into account.

???+ question "New `code/run_templates/orchestrator_tutorial_2` folder"
    To keep a clean distinction on the code of the previous tutorial and this one, 
    we will refer to the folder `code/run_templates/orchestrator_tutorial_2` 
    which is an exact copy of the folder `code/run_templates/orchestrator_tutorial_1`.
    
    You can create it by using the following command:
    ```bash title="copy `orchestrator_tutorial_1`"
    cp -r code/run_templates/orchestrator_tutorial_1 code/run_templates/orchestrator_tutorial_2
    ```

```json title="code/run_templates/orchestrator_tutorial2/run.json" linenums="1" hl_lines="3-35 40-43 47 51 56-58 66 75"
--8<-- "tutorial/advanced_cosmotech_simulator/run.json"
```

We can see a few changes and additions compared to the previous `run.json` file:

- We created a new `step` called `DownloadScenarioData` that makes use of `csm-orc fetch-scenariorun-data`:
    + In this step we defined a few environment variables required to run it, 
      but we still added `useSystemEnvironment` to `true` to ensure any environment variable required 
      to connect to the API is made available as well.
- In the `ApplyParameters` we made a few changes:
    + `DATASET/PARAMETERS_PATH` became `CSM_DATASET/PARAMETERS_ABSOLUTE_PATH`.
    + We added `/parameters.json` in the arguments for the parameters path.
    + We added a precendent step to schedule it after the
    `DownloadScenarioData`.
- In the `SimulatorRun` step changes are minimal:
    + The template targeted is the new `orchestrator_tutorial_2`.
    + The default value of `CSM_SIMULATION` has been changed to `BusinessApp_Simulation` 
      since `docker` simulation can't make use of visual consumers.

## Build a docker image

Now that we have our `run.json` ready we can build our docker image.

```bash title="Build a docker image using csmcli"
# First we will clean everything to ensure a correct generation of the project
csm clean
# Now we can build our full project
csm flow
# The simulator is now ready to be packaged
csm docker build
```

After running those commands we end up with a docker image `cosmotech/mybrewery_simulator` ready to be used.

A simple test can be made with the following command:

```bash title="Test the docker image"
docker run -e CSM_RUN_TEMPLATE_ID=orchestrator_tutorial_1 -e CSM_SIMULATION=BusinessApp_Simulation -v ./Simulation/Resource/scenariorun-data:/mnt/scenariorun-data cosmotech/mybrewery_simulator
```

!!! question "About the parameters of the command `docker run`"
    - `-e` sets an environment variable during the docker run, here we set our run template id and our simulation.
    - `-v` sets a volume during the docker run, 
      here we mount our local `Simulation/Resource/scenariorun-data` folder to the path `/mnt/scenariorun-data` 
      in the `docker` container, allowing us to use our existing dataset during the run.

## Define API items

The following sections give you simple examples of `.yaml` files used to define resources in the Cosmo Tech API.

### Define a `Solution`

An example of `Solution.yaml` (a file used by the Cosmo Tech API) for our current solution would be:

```yaml title="Solution.yaml"
--8<-- "tutorial/advanced_cosmotech_simulator/Solution.yaml:config"
--8<-- "tutorial/advanced_cosmotech_simulator/Solution.yaml:parameters"
--8<-- "tutorial/advanced_cosmotech_simulator/Solution.yaml:runTemplates"
```

Full Open API description of a `Solution` is available [here](https://raw.githubusercontent.com/Cosmo-Tech/cosmotech-api/main/solution/src/main/openapi/solution.yaml).
??? info "Open API description of a Solution (`components.schemas`)"
    ```yaml linenums="1"
    --8<-- "https://raw.githubusercontent.com/Cosmo-Tech/cosmotech-api/main/solution/src/main/openapi/solution.yaml:649:988"
    ```

Once this file is sent to a Cosmo Tech API we will get a `Solution ID` of the form `sol-xxxxxxxx`
which will allow us to create further elements inside the API referencing our solution.

Now let's look deeper at how to create our `Solution.yaml`.

#### `Solution` description

```yaml title="Solution.yaml - description"
--8<-- "tutorial/advanced_cosmotech_simulator/Solution.yaml:config"
```

We can see a few important properties in this part of the `Solution` file:

* `key`: it is a "grouping" value used to make multiple `Solution` using the same base but different versions together.
* `name`: a simple name given to the `Solution`.
* `description`: a simple description of the `Solution`.
* `tags`: a list of tags used in the API to filter `Solution` resources.
* `repository`: the name of the `docker` image inside the image registry.
* `version`: the version of the `docker` image tied to the `Solution`.

#### `parameters` and `parameterGroups`

```yaml title="Solution.yaml - parameters"
--8<-- "tutorial/advanced_cosmotech_simulator/Solution.yaml:parameters"
```

In this part we declare our scenario parameters. As previously decided we need three parameters:

* `NbWaiters`
* `RestockQty`
* `Stock`

Each parameter can be given a type (property `varType`) and a default value (property 'defaultValue').
Then we grouped our `parameters` in a `parametersGroup` "bar_parameters". Parameter groups will make our parameters available in further part of the `Solution`.

#### `runTemplates`

```yaml title="Solution.yaml - runTemplates"
--8<-- "tutorial/advanced_cosmotech_simulator/Solution.yaml:runTemplates"
```

In this part we finally define our `Run Template` for the API. We have three main elements to define:

* `id`: the `id` of a run template is the name of a folder inside `code/run_templates` that will contain a `run.json` file, along with one sub-folder for each step in the run template.
* `parameterGroups`: list of parameter groups available for the run template. Parameters declared in those groups can be changed by users in order to create new scenarios.
* `csmSimulation`: the name of a simulation file (without the ```.sml.xml``` suffix), to be set in the `CSM_SIMULATION_ID` environment variable. This simulation will run as part of the run template execution.

### Define a `Workspace`

An example of `Workspace.yaml` which is a file used by the Cosmo Tech API for our current solution would be:

```yaml title="Workspace.yaml"
--8<-- "tutorial/advanced_cosmotech_simulator/Workspace.yaml"
```

Full Open API description of a `Workspace` is available [here](https://raw.githubusercontent.com/Cosmo-Tech/cosmotech-api/main/workspace/src/main/openapi/workspace.yaml).
??? info "Open API description of a Workspace (`components.schemas`)"
    ```yaml linenums="1"
    --8<-- "https://raw.githubusercontent.com/Cosmo-Tech/cosmotech-api/main/workspace/src/main/openapi/workspace.yaml:692:854"
    ```

!!! warning "After creating a `Workspace` resource using the API you will need to create additional resources for it in your platform if you want to run scenarios."

Once your `Workspace` is created you will get a workspace identifier of the form `w-xxxxxxxx`. It will allow you to connect to your workspace and reference it in other resources.

We have 3 required parts in a `Workspace`:

* `key`: a unique identifier for your workspace which will be used during resource creation.
* `name`: the name of your `Workspace`.
* `solution.solutionId`: the solution identifier (`sol-xxxxxxxx`) for the solution you want to use in your workspace.

### Define a `Dataset`

An example of `Dataset.yaml` which is a file used by the Cosmo Tech API for our current solution would be:

```yaml title="Dataset.yaml"
--8<-- "tutorial/advanced_cosmotech_simulator/Dataset.yaml"
```

Full Open API description of a `Dataset` is available [here](https://raw.githubusercontent.com/Cosmo-Tech/cosmotech-api/main/dataset/src/main/openapi/dataset.yaml).
??? info "Open API description of a Dataset (`components.schemas`)"
    ```yaml linenums="1"
    --8<-- "https://raw.githubusercontent.com/Cosmo-Tech/cosmotech-api/main/dataset/src/main/openapi/dataset.yaml:1191:1560"
    ```

A `Dataset` is defined by a name, a type of data source (property `sourceType`) and a twin
graph identifier (property `twingraphId`).
After creating your `Dataset` you will get an identifier of the form `d-xxxxxxxx` which will be used to reference it to your scenarios.

### Define a `Scenario`

An example of `Scenario.yaml` which is a file used by the Cosmo Tech API for our current solution would be :

```yaml title="Scenario.yaml"
--8<-- "tutorial/advanced_cosmotech_simulator/Scenario.yaml"
```

Full Open API description of a `Scenario` is available [here](https://raw.githubusercontent.com/Cosmo-Tech/cosmotech-api/main/scenario/src/main/openapi/scenario.yaml)
??? info "Open API description of a Scenario (`components.schemas`)"
    ```yaml linenums="1"
    --8<-- "https://raw.githubusercontent.com/Cosmo-Tech/cosmotech-api/main/scenario/src/main/openapi/scenario.yaml:830:1126"
    ```

As a result of creating your `Scenario` you will get an identifier of the form `s-xxxxxxxx` that you can use to run it (as we will see further) and reference it in other endpoints.

A scenario essentially combines a run template with a dataset. The run template provides a set of parameters that can then be modified by the user before running the scenario. Multiple elements are required for defining a scenario, most notably:

* `runTemplateId`: should be one of the run template identifiers defined in our `Solution`.
* `datasetList`: should reference a previously defined `Dataset` using its identifier.
* `parametersValues`: is a list of objects representing the parameters we defined in the `Solution`, with the actual values they are set to.

## Run our distant `Scenario`

We will need to either use a lot of parameters or environment variables. To make
things easier we can make use of a parameter of `csm-orc run` to generate a template of `.env` file we will be able to use.

That parameter is `--gen-env-target` and takes a filename to create a `.env` file initialized with all the environment variables defined in our `run.json`

If a variable is set multiple times, only the last one will be taken into account. Each environment variable will have one and only one value from the following list (highest value in the list takes precedence):

- The `value` defined in the `run.json`.
- The current value in your working environment.
- The `defaultValue` defined in the `run.json`.
- The `description` defined in the `run.json`.
- `None` if no other value can be found.

```bash title="use of --gen-env-target"
csm-orc run code/run_templates/orchestrator_tutorial_2/run.json --gen-env-target code/run_templates/orchestrator_tutorial_2/vars.env
cat code/run_templates/orchestrator_tutorial_2/vars.env
# CSM_API_SCOPE=The scope of identification used to request access token for your Cosmo Tech API instance
# CSM_API_URL=The URL used to query your Cosmo Tech API instance
# CSM_DATASET_ABSOLUTE_PATH=Simulation/Resource/scenariorun-data
# CSM_ORGANIZATION_ID=The identifier of the organization in the Cosmo Tech API
# CSM_PARAMETERS_ABSOLUTE_PATH=code/run_templates/orchestrator_tutorial_2
# CSM_SCENARIO_ID=The identifier of the scenario in the Cosmo Tech API
# CSM_SIMULATION=BusinessApp_Simulation
# CSM_WORKSPACE_ID=The id of the workspace in the Cosmo Tech API
```

This `.env` file can then be used as a parameter of the `docker run` command with `--env-file` 
or can be used with a tool like `dotenv` (`pip install dotenv`) to temporary set the environment variables of commands. 
You can also just load it to get all values in your current environment.

=== "load a `.env` file in bash then run `csm-orc`"
    ```bash
    set -o allexport
    source code/run_templates/orchestrator_tutorial_2/vars.env set
    +o allexport
    csm-orc run code/run_templates/orchestrator_tutorial_2/run.json
    ```
=== "`docker run` with `.env`"
    ```bash
    docker run --env-file code/run_templates/orchestrator_tutorial_2/vars.env cosmotech/mybrewery_simulator
    ```
=== "`csm-orc run` with `.env` and `dotenv`"
    ```bash
    dotenv -e code/run_templates/orchestrator_tutorial_2/vars.env csm-orc run code/run_templates/orchestrator_tutorial_2/run.json
    ```

## I want to use my local data instead of needing a `Scenario`

The `csm-orc run` command comes with an optional parameter `--skip-step` that can be set 
in an environment variable `CSM_SKIP_STEPS`. This parameter can be given a list of steps that will be ignored during the run.

Since the "only" step used to download distant data from our run is `DownloadScenarioData` we can simply run locally by skipping it:

```bash title="Running only the SimulationRun step"
csm-orc run --skip-step DownloadScenarioData --skip-step ApplyParameters code/run_templates/orchestrator_tutorial_2/run.json
```


---
description: legacy tutorial to combine csm-orc and a Cosmo Tech Simulator
---
# Integration with a Cosmo Tech Simulator

!!! abstract "Objective"
    + Create an orchestration file for a Cosmo Tech Simulator
    + Use existing Solution info to generate an orchestration file and run it locally

!!! warning "Prerequisites"
    + You need to have completed the "Brewery" onboarding for Cosmo Tech projects
    + You need a local version of the "Brewery" solution (full code available [here](https://github.com/Cosmo-Tech/onboarding-brewery-solution))

--8<-- "partials/orchestrator_known_issues.md"

## Create a new orchestration file for a Run Template

In this first part we will look at creating a new orchestration file from scratch.

We will first initialize our run template folder

```bash title="create orchestrator_tutorial run template folder"
mkdir code/run_templates/orchestrator_tutorial
```

??? info
    By creating it inside the `code/run_templates` folder we will make it packaged in future docker images

### Write a `parameters` file

We will create a set of parameters, make them available for the `what_if` parameter handler defined during the onboarding and then run our simulator.

To initialize our parameters, we will use a helper command of `csm-orc` : `init-parameters`

During the onboarding we created the file `API/Solution.yaml` that contains the API definition of the Solution and the parameters we will be using it to initialize our parameters file. 

```bash title="Initialize parameters.json"
csm-orc init-parameters solution API/Solution.yaml code/run_templates/orchestrator_tutorial/parameters what_if --no-write-csv --write-json
```

After running this command we have a folder `orchestrator_tutorial` initialized with our `parameters` folder and a `parameters.json` file

```json title="code/run_templates/orchestrator_tutorial/parameters/parameters.json" linenums="1"
--8<-- "tutorial/brewery/parameters/parameters_init.json"
```

In the file we can see 3 lines with the `value` property set to a dummy one (for example `#!json "value": "stock_value"`), we need to set those variables before being able to use them.

```json title="updated parameters.json" linenums="1" hl_lines="4 10 16"
--8<-- "tutorial/brewery/parameters/parameters.json"
```

Before moving on we will create a folder `dataset` in the `orchestrator_tutorial` folder for future use

```bash
mkdir code/run_templates/orchestrator_tutorial/dataset
```

Now that we have a `orchestrator_tutorial` folder ready to be used we can start working on our orchestration file.

### Define our set of commands

But first we will define which commands we want to run before orchestrating them.

For simplicity, we will be using helper commands made available with `csm-orc` again so that we can keep commands close to the cloud environment.

To run our steps we will make use of the `run-step` command.

In the Brewery onboarding you created a run template called  `what_if`; we will use its code with no modification.

The `parameters_handler` part makes use of 2 environment variables (defined in its code) :

+ `CSM_DATASET_ABSOLUTE_PATH` : a path to our dataset  
+ `CSM_PARAMETERS_ABSOLUTE_PATH` : a path to our parameters

We previously created the content of our `orchestrator_tutorial` folder we will be using it there to make our data available.

One last step will be to copy the content of our dataset in the folder.

```bash title="run parameter handler step"
cp Simulation/Resource/scenariorun-data/* code/run_templates/orchestrator_tutorial/dataset
export CSM_DATASET_ABSOLUTE_PATH="code/run_templates/orchestrator_tutorial/dataset"
export CSM_PARAMETERS_ABSOLUTE_PATH="code/run_templates/orchestrator_tutorial/parameters"
csm-orc run-step --template what_if --steps parameters_handler
```

By taking a look at the values of the `code/run_templates/orchestrator_tutorial/dataset/Bar.csv` file we can see that our `parameters_handler` worked.

The next step will be to run our simulation and get our data out of it.

We will once more make use of the `run-step` command to run the `engine` step, it is a specific step that runs the simulator directly

Before running the `engine` step we need to back up our existing `Simulation/Resource/scenariorun-data` folder if it exists, and restore it at the end.

Then we will copy our dataset in the now empty folder.

!!! warning
    A limitation on the language makes it required to manually change the dataset we want to use during a simulation.  
    The loader targets the folder `Simulation/Resource/scenariorun-data` to load the simulation, 
    thus we will back it up to keep our original dataset replace the content with our new data and run the simulation 
    before replacing the back-up in its original folder.

```bash title="code/run_templates/orchestrator_tutorial/replace_scenariorun_data.sh"
--8<-- "tutorial/brewery/replace_scenariorun_data.sh"
```

```bash title="code/run_templates/orchestrator_tutorial/restore_scenariorun_data.sh"
--8<-- "tutorial/brewery/restore_scenariorun_data.sh"
```

Using the environment variable `CSM_Simulation` we can control which simulation to run.

```bash title="run simulation"
export CSM_SIMULATION="CSV_Simulation"
csm-orc run-step --template what_if --steps engine
```

Using those 3 commands we are now able to run a local simulation and set back our state.

We now have been able to apply our parameter handler and then run our simulation using 3 environment variables, 
we are ready to write our orchestration file.

### Writing the orchestration file

Following the previous tutorials it is easy to write a simple orchestration file :

```json title="code/run_templates/orchestrator_tutorial/run.json" 
--8<-- "tutorial/brewery/run.json"
```

!!! warning
    In the `engine` step we set the field `#!json "useSystemEnvironment": true`, 
    it allows to use the system environment variables that are set for graphical interfaces.
    Without it (or if set to `#!json false`) we would have crashes with the simulator when using the QT Consumers locally.
    
    :warning: In a docker environment we won't have access to a graphical interface, so even with this field the QT Consumers will crash.


We can then easily run this file :

```bash title="run run.json" 
export CSM_DATASET_ABSOLUTE_PATH="code/run_templates/orchestrator_tutorial/dataset"
export CSM_PARAMETERS_ABSOLUTE_PATH="code/run_templates/orchestrator_tutorial/parameters"
export CSM_SIMULATION="CSV_Simulation"
csm-orc run code/run_templates/orchestrator_tutorial/run.json
```
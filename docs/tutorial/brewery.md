# Integration with a CosmoTech Simulator

!!! abstract "Objective"
    + Create an orchestration file for a CosmoTech Simulator
    + Use existing Solution info to generate an orchestration file and run it locally

!!! warning "Prerequisites"
    + You need to have completed the "Brewery" onboarding for CosmoTech projects
    + You need a local version of the "Brewery" solution (available [here](https://github.com/Cosmo-Tech/onboarding-brewery-solution))

--8<-- "docs/partials/orchestrator_known_issues.md"

## Create a new orchestration file for a Run Template

In this first part we will look at creating a new orchestration file from scratch.

### Write a `parameters` file

We will create a set of parameters, make them available for the `what_if` parameter handler defined during the onboarding and then run our simulator.

To initialize our parameters, we will use a helper command of `csm-run-orchestrator` : `init-parameters`

During the onboarding we created the file `API/Solution.yaml` that contains the API definition of the Solution and the parameters we will be using it to initialize our parameters file. 

```bash title="Initialize parameters.json"
csm-run-orchestrator init-parameters solution API/Solution.yaml tutorial/parameters what_if --no-write-csv --write-json
```

After running this command we have a folder `tutorial` initialized with our `parameters` folder and a `parameters.json` file

```json title="code/tutorial/parameters/parameters.json" linenums="1"
--8<-- "tutorial/brewery/parameters/parameters_init.json"
```

In the file we can see 3 lines with the `value` property set to a dummy one (for example `#!json "value": "stock_value"`), we need to set those variables before being able to use them.

```json title="updated parameters.json" linenums="1" hl_lines="4 10 16"
--8<-- "tutorial/brewery/parameters/parameters.json"
```

Before moving on we will create a folder `dataset` in the `tutorial` folder for future use

```bash
mkdir tutorial/dataset
```

Now that we have a `tutorial` folder ready to be used we can start working on our orchestration file.

### Define our set of commands

But first we will define which commands we want to run before orchestrating them.

For simplicity, we will be using helper commands made available with `csm-run-orchestrator` again so that we can keep commands close to the cloud environment.

To run our steps we will make use of the `run-step` command

The `parameters_handler` part make use of 2 environment variables (defined in its code) : 
- `CSM_DATASET_ABSOLUTE_PATH` : a path to our dataset
- `CSM_PARAMETERS_ABSOLUTE_PATH` : a path to our parameters

We previously created the content of our `tutorial` folder we will be using it there to make our data available.

One last step will be to copy the content of our dataset in the folder.

```bash title="run parameter handler step"
cp Simulation/Resource/scenariorun-data/* code/tutorial/dataset
export CSM_DATASET_ABSOLUTE_PATH="code/tutorial/dataset"
export CSM_PARAMETERS_ABSOLUTE_PATH="code/tutorial/parameters"
csm-run-orchestrator run-step --template what_if --steps parameters_handler
```

By taking a look at the values of the `tutorial/dataset/Bar.csv` file we can see that our `parameters_handler` worked.

The next step will be to run our simulation and get our data our of it.

We will once more make use of the `run-step` command to run the `engine` step, it is a specific step that runs the simulator directly

Before running the `engine` step we need to back up our existing `Simulation/Resource/scenariorun-data` folder if it exists, and restore it at the end.

Then we will copy our dataset in the now empty folder.

!!! warning
    A limitation on the language makes it required to manually change the dataset we want to use during a simulation.  
    The loader targets the folder `Simulation/Resource/scenariorun-data` to load the simulation, 
    thus we will back it up to keep our original dataset replace the content with our new data and run the simulation 
    before replacing the back-up in its original folder.

```bash title="Back up scenariorun-data"
if [ -d "Simulation/Resource/scenariorun-data/" ]; then
  mv Simulation/Resource/scenariorun-data/ Simulation/Resource/scenariorun-data.back
fi
cp -r $CSM_DATASET_ABSOLUTE_PATH/* Simulation/Resource/scenariorun-data/
```

```bash title="restore scenariorun-data"
if [ -d "Simulation/Resource/scenariorun-data.back/" ]; then
  rm -rf Simulation/Resource/scenariorun-data/ 
  mv Simulation/Resource/scenariorun-data.back Simulation/Resource/scenariorun-data 
fi
```

Using the environment variable `CSM_Simulation` we can control which simulation to run.

```bash title="run simulation"
export CSM_SIMULATION="CSV_Simulation"
csm-run-orchestrator run-step --template what_if --steps engine
```

Using those 3 commands we are now able to run a local simulation and set back our state.

Everything can be run in a single action with the following script
```bash title="code/tutorial/run_engine.sh"
--8<-- "tutorial/brewery/run_engine.sh"
```

We now have been able to apply our parameter handler and then run our simulation using 3 environment variables, 
we are ready to write our orchestration file.

### Writing the orchestration file

Following the previous tutorials it is easy to write a simple orchestration file :

```json title="code/tutorial/simple_orchestration.json" 
--8<-- "tutorial/brewery/simple_orchestration.json"
```

!!! warning
    In the `engine` step we set the field `#!json "useSystemEnvironment": true`, 
    it allows to use the system environment variables that are set for graphical interfaces.
    Without it (or if set to `#!json false`) we would have crashes with the simulator when using the QT Consumers locally.
    
    :warning: In a docker environment we won't have access to a graphical interface, so even with this field the QT Consumers will crash.


We can then easily run this file :

```bash title="run simple_orchestration.json" 
export CSM_DATASET_ABSOLUTE_PATH="code/tutorial/dataset"
export CSM_PARAMETERS_ABSOLUTE_PATH="code/tutorial/parameters"
export CSM_SIMULATION="CSV_Simulation"
csm-run-orchestrator orchestrator code/tutorial/simple_orchestration.json
```
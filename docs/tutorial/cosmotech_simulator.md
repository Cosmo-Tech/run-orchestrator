---
description: Simple tutorial to combine csm-orc and a Cosmo Tech Simulator
---
# Integration with a Cosmo Tech Simulator

!!! abstract "Objective"
    + Combine previous tutorials and Cosmo Tech Simulator to be able to apply changes to a simulation instance.

!!! warning "Prerequisites"
    + You need to have completed the "Brewery" onboarding for Cosmo Tech projects.
    + You need a local version of the "Brewery" solution (full code available [here](https://github.com/Cosmo-Tech/onboarding-brewery-solution)).

--8<-- "partials/orchestrator_known_issues.md"

## Reminder : Model + Project

The full simulator files can be found with the tag 
[Complete-model](https://github.com/Cosmo-Tech/onboarding-brewery-solution/releases/tag/Complete-model)
on the repository.

Online view: [here](https://github.com/Cosmo-Tech/onboarding-brewery-solution/blob/Complete-model/ConceptualModel/MyBrewery.csm.xml)

```text title="Project files"
--8<-- "tutorial/cosmotech_simulator/repo_tree_initial.txt"
```

The Brewery conceptual model is very simple: it consists of a Bar entity and a Customer entity, 
where the Bar contains the Customer(s). 
The Bar can serve the Customers based on customer thirst levels and stock. 
It restocks when stock drops below a set restock quantity.

Customers have a Thirsty state and a Satisfaction state, which affect each other: 
the higher the satisfaction, the higher the chance of becoming thirsty, 
and the longer a customer is left thirsty, the lower the satisfaction. 
Satisfaction increases when a customer is served. 
Satisfaction is also affected by the satisfaction of surrounding customers.

For this tutorial we will write our new files in the folder `MyBrewery/code/run_templates/orchestrator_tutorial_1` (this folder hierarchy will be used in future tutorials too).

## Define a set of parameters to apply

In our simulation we will want to see the effects of variations on the Bar attributes.

Our existing CSV based simulations look for 3 attributes to instantiate a Bar:

* `NbWaiters`: the number of waiters in our Bar
* `RestockQty`: the quantity of elements to restock when getting below the threshold
* `Stock`: the Bar initial stock

We will then use those 3 attributes as parameters for our simulations.

To store our parameters we will define a JSON file containing them. 

```json title="code/run_templates/orchestrator_tutorial_1/parameters.json"
--8<-- "tutorial/cosmotech_simulator/parameters.json"
```

???+ info "About the JSON file format"
    In prevision of future use, we will define a json format close to the one returned by the command:  
    ```bash
    csm-orc fetch-scenariorun-data
    ```  
    This command will be used later to download data from the Cosmo Tech API.

## Apply our parameters

Having defined our 3 parameters we can now work on a script to apply those to update a given dataset

Our script will consist of 3 steps:

- Read the original dataset
- Apply our parameters to the dataset
- Write the new dataset in a given folder

We will need 3 parameters for the script:

- The path to our original dataset
- The path to our parameter file
- The path where we want to write our new dataset

Using those information we can write a simple script:

```python title="code/run_templates/orchestrator_tutorial_1/apply_parameters.py"
--8<-- "tutorial/cosmotech_simulator/apply_parameters.py"
```

Using that script can do the trick, we can test it :

```bash title="Test run of apply_parameters.py"
python code/run_templates/orchestrator_tutorial_1/apply_parameters.py Simulation/Resource/scenariorun-data code/run_templates/orchestrator_tutorial_1/scenariorun-data code/run_templates/orchestrator_tutorial_1/parameters.json
cat code/run_templates/orchestrator_tutorial_1/scenariorun-data/Bar.csv
# NbWaiters,RestockQty,Stock,id
# 89,4567,123,MyBar
```

We can see that having run the script our `Bar.csv` got correctly updated with our parameters.

## Run a simulation with our updated parameters

A limitation on the CoSML language locks the folder used by a simulation to load datasets from. 
In the existing model the file `Simulation/Resource/CSV_Brewery.ist.xml` sets this folder to `Simulation/Resource/scenariorun-data`.
We will have to use that folder to give the simulator access to our dataset.

??? info "About `Simulation/Resource/scenariorun-data`"
    The folder `Simulation/Resource/scenariorun-data` is a special folder:
    in Cosmo Tech cloud platform (where solutions are packaged as Docker containers), 
    this folder is replaced by a symbolic link to the path `/mnt/scenariorun-data` 
    which is in an environment variable called `CSM_DATASET_ABSOLUTE_PATH`.
    
    We then know that the content of this folder will not be available in a container as is, 
    and need to keep that in mind for future uses.

For simplicity, we won't be making an effort to keep the old values of possibly existing datasets and will overwrite the content instead.

It will be attained by using our `apply_parameters.py` on the same input and output folder (here `Simulation/Resource/scenariorun-data`)

A safer way would be to make a back-up of the dataset and to restore it after the run, but we won't go over this possibility in this tutorial.

To run the simulator we can either make use of `csmcli`, the `main` executable or `csm-orc run-step`; we will only cover the `csm-orc` use in this tutorial.

By writing our code in the folder `code/run_templates/orchestrator_tutorial_1` we declared a Run Template named `orchestrator_tutorial_1` that we can call in `csm-orc` commands.

The simulator run can be configured by using some options of the `csm-orc run-step` command:

- `--template orchestrator_tutorial_1` is necessary to target a run template (dependency for non-simulator run steps)
- `--steps engine` will either look for a file `engine/main.py` in target run template or (if not found and the environment variable `CSM_SIMULATION` is set) try to run the simulator using a CoSML simulation file.

So the following command will run our `CSV_Simulation` defined by the `Simulation/CSV_Simulation.sml.xml`:

```bash title="run CSV_Simulation using csm-orc"
CSM_SIMULATION=CSV_Simulation csm-orc run-step --template orchestrator_tutorial_1 --steps engine
```

Since we did not update our dataset files in place of the original ones (only the `engine` step was executed) we will get our usual simulation results.

Now we can simply run both commands to update our dataset then run the updated simulation:

```bash title="Apply parameters and run simulation"
python code/run_templates/orchestrator_tutorial_1/apply_parameters.py Simulation/Resource/scenariorun-data Simulation/Resource/scenariorun-data code/run_templates/orchestrator_tutorial_1/parameters.json
CSM_SIMULATION=CSV_Simulation csm-orc run-step --template ochestrator_tutorial_1 --steps engine 
```

A different set of charts should appear this time, corresponding to our updated dataset values..

Now we can write our `run.json` file to run those step in a single command.

```bash title="core/run_templates/orchestrator_tutorial_1/run.json"
--8<-- "tutorial/cosmotech_simulator/run.json"
```

Now that we have this `run.json` file we can run it:
```bash title="run run.json"
csm-orc run code/run_templates/orchestrator_tutorial_1/run.json
```

And we are done! Our first simulation based on our parameters file ran in a single command. :)

You can now do the next tutorial: "Make a Cosmo Tech Simulator cloud-ready".

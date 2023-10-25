---
description: Simple tutorial to discover csm-orc 
---
# My first orchestration

!!! abstract "Objective"
    + Set up an orchestration project
    + Create a few scripts to organize
    + Create an orchestration file to run our scripts

## Setting up our project

During this tutorial we will start from a clean installation of `csm-orc` and work our way to an
orchestrated solution.

```bash title="Set up our project"
# First we will create a new folder for our project
mkdir MyFirstOrchestrationProject
cd MyFirstOrchestrationProject
# Now that we are in our project folder we will set up the orchestrator using a python venv
# We create the venv in the folder `.venv`
python -m venv .venv
# We activate the venv
. .venv/bin/activate
# Now we can install the orchestrator using pip
pip install cosmotech-run-orchestrator
# We can check that our installation worked by running the orchestrator help
csm-orc --help
```

After all that our project is ready to start

## Creating our first scripts

In this part we will create 2 simple python script that will interact by using a common file,
the first script should write the first N members of the Fibonacci sequence on the file,
and the second one will display them.

=== "Fibonacci"
    ```python title="fibonacci.py" linenums="1"
    --8<-- "tutorial/first/fibonacci.py"
    ```

=== "Display"
    ```python title="display_file.py" linenums="1"
    --8<-- "tutorial/first/display_file.py"
    ```

!!! example "Let's try our scripts"
    Running those two files is easy
    ```bash
    python fibonacci.py 10 fib.txt
    python display_file.py fib.txt
    ```
    This should display the following lines
    ```
    0
    1
    1
    2
    3
    5
    8
    13
    21
    34
    ```

## Write a first orchestration

Now that we have our two files, we want to create an orchestration file to run them.

An orchestration file is a json file following the given JSON schema

??? info "JSON-schema"
    The following schema can be impressive, but we will go through most of it in the next points.
    ```json title="JSON-schema" linenums="1"
    --8<-- "cosmotech/orchestrator/schema/run_template_json_schema.json"
    ```

### The first step

In the schema we can see that it is divided in two parts :

- the CommandTemplate
- the Step

For this first orchestration file we will only use steps.

Let's take a look at an example step


```json title="simple_step.json" linenums="1"
--8<-- "tutorial/first/simple_step.json"
```

In this minimal file we can see one `step` with the id `echo-foo-bar` 
that runs the command `echo` with the arguments `foo` and `bar`.

This orchestration file is valid following the JSON schema as we have at least 1 element in `steps`, and the element as at least an `id` and a `command`

We can run this orchestration file with the following command :

```bash title="run simple_step.json" linenums="1"
csm-orc run simple_step.json
# [YYYY/MM/DD-HH:mm:SS] INFO     ===      Run     ===
# [YYYY/MM/DD-HH:mm:SS] INFO     Starting step echo-foo-bar
# foo bar
# [YYYY/MM/DD-HH:mm:SS] INFO     Done running step echo-foo-bar
# [YYYY/MM/DD-HH:mm:SS] INFO     ===     Results    ===
# [YYYY/MM/DD-HH:mm:SS] INFO     echo-foo-bar (Done)
```

On line 4 we can see the result of the command `echo foo bar` which is defined in the step.

Now using this basis we will write our commands in an orchestration file using the same options as the previous example

!!! example "Let's try our scripts as an orchestration file"
    ```json title="run.json" linenums="1"
    --8<-- "tutorial/first/run.json"
    ```
    Now we can run our file using the orchestrator
    ```bash title="run our first orchestration"
    csm-orc run run.json
    ```

In the example `run.json` you can see on line 12 the apparition of the key-words `precedents`, 
it is used to order our operations.

Here by setting the step `run-fibo` as a precedent to the step `run-display` 
we ensure that the first script will run before the second.

And now we created a simple example of orchestration file to run some of our scripts.
In the next tutorial we will look at how to use CommandTemplates to re-use possibly complex commands, and Environment Variables to change the effect of our commands.
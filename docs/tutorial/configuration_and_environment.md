---
description: Simple tutorial to learn about Environment Variables and csm-orc
---
# Concerning configuration


!!! abstract "Objective"
    + Add environment variables to our script
    + Use environment variables in our orchestration
    + Use CommandTemplate to combine close commands


???+ info "Use of `dotenv`"

    In most scenarios you may want to have capabilities of controling your environment variables, you can install the python package `dotenv-cli` for ease of use

    On UNIX system you can make a "global" installation of this cli by running the following commands :

    ```bash
    cd ~
    python -m venv dotenv_venv
    source dotenv_venv/bin/activate
    pip install dotenv-cli
    ln -s ~/dotenv_venv/bin/dotenv ~/.local/bin/dotenv
    ```

    Running those will make the `dotenv` command available everywhere for your session

## Taking a look at Environment Variables

We will start in the same folder as the previous tutorial : `MyFirstOrchestrationProject`
and augment it to use some Environment Variables to configure our commands.

First we will start by modifying our scripts to now accept an environment variable for the file path

=== "Fibonacci"
    ```python title="fibonacci.py" linenums="1" hl_lines="2 8 11"
    --8<-- "tutorial/configuration_and_environment/fibonacci.py"
    ```

=== "Display"
    ```python title="display_file.py" linenums="1" hl_lines="2 5 8"
    --8<-- "tutorial/configuration_and_environment/display_file.py"
    ```

Those modifications will allow us to set an Environment Variable `FIBO_FILE_PATH` that will be used for our file name

!!! example "Let's try our scripts"
    Running those two files is easy
    ```bash
    export FIBO_FILE_PATH=fib_second.txt
    python fibonacci.py 10
    python display_file.py
    ```
    Without environment variable we would run the following commands
    ```bash
    python fibonacci.py 10 --filename fib_second.txt
    python display_file.py --filename fib_second.txt
    ```
    Both ways should display the following lines
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

Now that our commands work we will look at the orchestration file to configure those environment variables

```json title="run_env.json" hl_lines="6-11 16 18-21"
--8<-- "tutorial/configuration_and_environment/run_env.json"
```

We added 2 definitions of our `FIBO_FILE_PATH` to the steps, so we can try to run our script

```bash title="Run the orchestrator without the environment variable"
# First we remove the definition of FIBO_FILE_PATH from the environment for the example
unset FIBO_FILE_PATH
csm-orc run run_env.json
# [YYYY/MM/DD-HH:mm:SS] ERROR    Missing environment values
# [YYYY/MM/DD-HH:mm:SS] ERROR     - FIBO_FILE_PATH
# [YYYY/MM/DD-HH:mm:SS] ERROR    Missing environment variables, check the logs
```

We can see that without defining our environment variable issues are displayed before the run.

If we wanted to know which environment variables are required for our orchestration script we can do the following

```bash title="Getting information about environment variables"
csm-orc run run_env.json --display-env
# [YYYY/MM/DD-HH:mm:SS] INFO     Environment variable defined for run_env.json
# [YYYY/MM/DD-HH:mm:SS] INFO      - FIBO_FILE_PATH:
#                                   - A file run-fibo will write to
#                                   - A file run-display will read and print to stdout
```

We can see that all descriptions of a variable are made available.

Let's give a value to `FIBO_FILE_PATH` and run our command

```bash title="Run the orchestrator with the environment variable"
FIBO_FILE_PATH=fib_second.txt csm-orc run run_env.json
# [YYYY/MM/DD-HH:mm:SS] INFO     ===      Run     ===
# [YYYY/MM/DD-HH:mm:SS] INFO     Starting step run-fibo
# [YYYY/MM/DD-HH:mm:SS] INFO     Done running step run-fibo
# [YYYY/MM/DD-HH:mm:SS] INFO     Starting step run-display
# 0
# 1
# 1
# 2
# 3
# 5
# 8
# 13
# 21
# 34
# [YYYY/MM/DD-HH:mm:SS] INFO     Done running step run-display
# [YYYY/MM/DD-HH:mm:SS] INFO     ===     Results    ===
# [YYYY/MM/DD-HH:mm:SS] INFO     run-fibo (Done)
# [YYYY/MM/DD-HH:mm:SS] INFO     run-display (Done)
```

We can see that our orchestrator works now.

## Use Environment Variables as Argument

To add more configuration to our file lets use an environment variable for the `run-fibo` step argument.

```json title="run_env_arg.json" hl_lines="6 11-14"
--8<-- "tutorial/configuration_and_environment/run_env_arg.json"
```

In this file we defined an environment variable that will be used as an argument for our command (by using it as an argument preceded by `$`),
that way we don't need to modify our script.

We also defined a `defaultValue` for the argument,
ensuring that even if the environment variable is not defined a default value is used.

=== "Run without the new variable"
    ```bash title="Run as previously"
    export FIBO_FILE_PATH=fib_second.txt
    csm-orc run run_env_arg.json
    # [YYYY/MM/DD-HH:mm:SS] INFO     ===      Run     ===
    # [YYYY/MM/DD-HH:mm:SS] INFO     Starting step run-fibo
    # [YYYY/MM/DD-HH:mm:SS] INFO     Done running step run-fibo
    # [YYYY/MM/DD-HH:mm:SS] INFO     Starting step run-display
    # 0
    # 1
    # 1
    # 2
    # 3
    # 5
    # 8
    # 13
    # 21
    # 34
    # [YYYY/MM/DD-HH:mm:SS] INFO     Done running step run-display
    # [YYYY/MM/DD-HH:mm:SS] INFO     ===     Results    ===
    # [YYYY/MM/DD-HH:mm:SS] INFO     run-fibo (Done)
    # [YYYY/MM/DD-HH:mm:SS] INFO     run-display (Done)
    ```

=== "Run with the new variable"
    ```bash title="Run the orchestrator with the new environment variable"
    export FIBO_FILE_PATH=fib_second.txt
    export FIBO_COUNT=8
    csm-orc run run_env_arg.json
    # [YYYY/MM/DD-HH:mm:SS] INFO     ===      Run     ===
    # [YYYY/MM/DD-HH:mm:SS] INFO     Starting step run-fibo
    # [YYYY/MM/DD-HH:mm:SS] INFO     Done running step run-fibo
    # [YYYY/MM/DD-HH:mm:SS] INFO     Starting step run-display
    # 0
    # 1
    # 1
    # 2
    # 3
    # 5
    # 8
    # 13
    # [YYYY/MM/DD-HH:mm:SS] INFO     Done running step run-display
    # [YYYY/MM/DD-HH:mm:SS] INFO     ===     Results    ===
    # [YYYY/MM/DD-HH:mm:SS] INFO     run-fibo (Done)
    # [YYYY/MM/DD-HH:mm:SS] INFO     run-display (Done)
    ```

## Use CommandTemplate to reduce copy

We now have 2 `steps` that use the same base `command` and a common Environment Variable.
Let's make use of the `CommandTemplate` to reduce the number of time we need to impact our steps.

```json title="run_with_template.json" hl_lines="5 16 21-31"
--8<-- "tutorial/configuration_and_environment/run_with_template.json"
```

We grouped the common part of the steps in a new command template called `python-with-fibo-file`,
then replaced the `command` of our steps by its `commandId`.

Now we can call the new file as previously

```bash title="Run the orchestrator with a command template"
export FIBO_FILE_PATH=fib_second.txt
export FIBO_COUNT=8
csm-orc run run_with_template.json
# [YYYY/MM/DD-HH:mm:SS] INFO     ===      Run     ===
# [YYYY/MM/DD-HH:mm:SS] INFO     Starting step run-fibo
# [YYYY/MM/DD-HH:mm:SS] INFO     Done running step run-fibo
# [YYYY/MM/DD-HH:mm:SS] INFO     Starting step run-display
# 0
# 1
# 1
# 2
# 3
# 5
# 8
# 13
# [YYYY/MM/DD-HH:mm:SS] INFO     Done running step run-display
# [YYYY/MM/DD-HH:mm:SS] INFO     ===     Results    ===
# [YYYY/MM/DD-HH:mm:SS] INFO     run-fibo (Done)
# [YYYY/MM/DD-HH:mm:SS] INFO     run-display (Done)
```

Now you can create command templates, use environment variables to configure your scripts, and set some values for those.

## Make use of optional Environment Variables

In some case you may want to have optional effects that can be used to change your script only if present
(the use of a `defaultValue` does not make sense for those)

For example, we will make a change to the run-display step to either print the content of the file as is,
or if an Environment Variable `DISPLAY_SYMBOL` is set it will instead display that symbol on each line X times,
where X is the number read from the file.

So `DISPLAY_SYMBOL=X` and `FIBO_COUNT=5` would look like that:

```text title="DISPLAY_SYMBOL=X and FIBO_COUNT=5"
#
# X
# X
# XX
# XXX
```

```python title="updated_display.py" linenums="1" hl_lines="10 17-21"
--8<-- "tutorial/configuration_and_environment/updated_display.py"
```

And to make use of that new script we can update our `.json` file as following

```json title="optional_envvar.json" hl_lines="18-23"
--8<-- "tutorial/configuration_and_environment/optional_envvar.json"
```

=== "Run without `DISPLAY_SYMBOL`"
    ```bash
    export FIBO_FILE_PATH=fib_second.txt
    export FIBO_COUNT=8
    csm-orc run optional_envvar.json
    # [YYYY/MM/DD-HH:mm:SS] INFO     ===      Run     ===
    # [YYYY/MM/DD-HH:mm:SS] INFO     Starting step run-fibo
    # [YYYY/MM/DD-HH:mm:SS] INFO     Done running step run-fibo
    # [YYYY/MM/DD-HH:mm:SS] INFO     Starting step run-display
    # 0
    # 1
    # 1
    # 2
    # 3
    # 5
    # 8
    # 13
    # [YYYY/MM/DD-HH:mm:SS] INFO     Done running step run-display
    # [YYYY/MM/DD-HH:mm:SS] INFO     ===     Results    ===
    # [YYYY/MM/DD-HH:mm:SS] INFO     run-fibo (Done)
    # [YYYY/MM/DD-HH:mm:SS] INFO     run-display (Done)
    ```

=== "Run with `DISPLAY_SYMBOL`"
    ```bash
    export FIBO_FILE_PATH=fib_second.txt
    export FIBO_COUNT=8
    export DISPLAY_SYMBOL=X
    csm-orc run optional_envvar.json
    # [YYYY/MM/DD-HH:mm:SS] INFO     ===      Run     ===
    # [YYYY/MM/DD-HH:mm:SS] INFO     Starting step run-fibo
    # [YYYY/MM/DD-HH:mm:SS] INFO     Done running step run-fibo
    # [YYYY/MM/DD-HH:mm:SS] INFO     Starting step run-display
    #
    # X
    # X
    # XX
    # XXX
    # XXXXX
    # XXXXXXXX
    # XXXXXXXXXXXXX
    # [YYYY/MM/DD-HH:mm:SS] INFO     Done running step run-display
    # [YYYY/MM/DD-HH:mm:SS] INFO     ===     Results    ===
    # [YYYY/MM/DD-HH:mm:SS] INFO     run-fibo (Done)
    # [YYYY/MM/DD-HH:mm:SS] INFO     run-display (Done)
    ```

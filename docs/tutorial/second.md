# Concerning configuration


!!! abstract "Objective"
    + Add environment variables to our script
    + Use environment variables in our orchestration
    + Use CommandTemplate to combine close commands

## Taking a look at Environment Variables

We will start in the same folder as the previous tutorial : `MyFirstOrchestrationProject` 
and augment it to use some Environment Variables to configure our commands.

First we will start by modifying our scripts to now accept an environment variable for the file path

=== "Fibonacci"
    ```python title="fibonacci.py" linenums="1" hl_lines="2 8 11"
    --8<-- "tutorial/second/fibonacci.py"
    ```

=== "Display"
    ```python title="display_file.py" linenums="1" hl_lines="2 5 8"
    --8<-- "tutorial/second/display_file.py"
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

```json title="run_env.json" hl_lines="7-11 18-21"
--8<-- "tutorial/second/run_env.json"
```

We added 2 definitions of our `FIBO_FILE_PATH` to the steps, so we can try to run our script

```bash title="Run the orchestrator without the environment variable"
# First we remove the definition of FIBO_FILE_PATH from the environment for the example
unset FIBO_FILE_PATH
csm-run-orchestrator orchestrator run_env.json
# [YYYY/MM/DD-HH:mm:SS] ERROR    Missing environment values
# [YYYY/MM/DD-HH:mm:SS] ERROR     - FIBO_FILE_PATH 
# [YYYY/MM/DD-HH:mm:SS] ERROR    Missing environment variables, check the logs
```

We can see that without defining our environment variable issues are displayed before the run.

If we wanted to know which environment variables are required for our orchestration script we can do the following

```bash title="Getting information about environment variables"
csm-run-orchestrator orchestrator run_env.json --display-env
# [YYYY/MM/DD-HH:mm:SS] INFO     Environment variable defined for run_env.json
# [YYYY/MM/DD-HH:mm:SS] INFO      - FIBO_FILE_PATH:
#                                   - A file run-fibo will write to
#                                   - A file run-display will read and print to stdout
```

We can see that all descriptions of a variable are made available.

Let's give a value to `FIBO_FILE_PATH` and run our command

```bash title="Run the orchestrator with the environment variable"
FIBO_FILE_PATH=fib_second.txt csm-run-orchestrator orchestrator run_env.json
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
# [YYYY/MM/DD-HH:mm:SS] INFO     Step run-fibo
#                                Command: python fibonacci.py 10
#                                Environment:
#                                - FIBO_FILE_PATH: A file run-fibo will write to
#                                Status: Done
# [YYYY/MM/DD-HH:mm:SS] INFO     Step run-display
#                                Command: python display_file.py
#                                Environment:
#                                - FIBO_FILE_PATH: A file run-display will read and print to stdout
```

We can see that our orchestrator works now.

## Use Environment Variables as Argument

To add more configuration to our file lets use an environment variable for the `run-fibo` step argument.

```json title="run_env_arg.json" hl_lines="6 11-14"
--8<-- "tutorial/second/run_env_arg.json"
```

In this file we defined an environment variable that will be used as an argument for our command (by using it as an argument preceded by `$`), 
that way we don't need to modify our script.

We also defined a `defaultValue` for the argument, 
ensuring that even if the environment variable is not defined a default value is used.

=== "Run without the new variable"
    ```bash title="Run as previously"
    export FIBO_FILE_PATH=fib_second.txt
    csm-run-orchestrator orchestrator run_env_arg.json
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
    # [YYYY/MM/DD-HH:mm:SS] INFO     Step run-fibo
    #                                Command: python fibonacci.py 10
    #                                Environment:
    #                                - FIBO_FILE_PATH: A file run-fibo will write to
    #                                - FIBO_COUNT: The rank of the fibonacci sequence run-fibo will write to
    #                                Status: Done
    # [YYYY/MM/DD-HH:mm:SS] INFO     Step run-display
    #                                Command: python display_file.py
    #                                Environment:
    #                                - FIBO_FILE_PATH: A file run-display will read and print to stdout
    ```

=== "Run with the new variable"
    ```bash title="Run the orchestrator with the new environment variable"
    export FIBO_FILE_PATH=fib_second.txt
    export FIBO_COUNT=8
    csm-run-orchestrator orchestrator run_env_arg.json
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
    # [YYYY/MM/DD-HH:mm:SS] INFO     Step run-fibo
    #                                Command: python fibonacci.py 10
    #                                Environment:
    #                                - FIBO_FILE_PATH: A file run-fibo will write to
    #                                - FIBO_COUNT: The rank of the fibonacci sequence run-fibo will write to
    #                                Status: Done
    # [YYYY/MM/DD-HH:mm:SS] INFO     Step run-display
    #                                Command: python display_file.py
    #                                Environment:
    #                                - FIBO_FILE_PATH: A file run-display will read and print to stdout
    ```

## Use CommandTemplate to reduce copy

We now have 2 `steps` that use the same base `command` and a common Environment Variable. 
Let's make use of the `CommandTemplate` to reduce the number of time we need to impact our steps.

```json title="run_with_template.json" hl_lines="5 16 21-31"
--8<-- "tutorial/second/run_with_template.json"
```

We grouped the common part of the steps in a new command template called `python-with-fibo-file`, 
then replaced the `command` of our steps by its `commandId`.

Now we can call the new file as previously

```bash title="Run the orchestrator with a command template"
export FIBO_FILE_PATH=fib_second.txt
export FIBO_COUNT=8 
csm-run-orchestrator orchestrator run_with_template.json
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
# [YYYY/MM/DD-HH:mm:SS] INFO     Step run-fibo
#                                Command: python fibonacci.py $FIBO_COUNT
#                                Environment:
#                                - FIBO_COUNT: The rank of the fibonacci sequence run-fibo will write to
#                                - FIBO_FILE_PATH: A file available to the command
#                                Status: Done
# [YYYY/MM/DD-HH:mm:SS] INFO     Step run-display
#                                Command: python display_file.py
#                                Environment:
#                                - FIBO_FILE_PATH: A file available to the command
#                                Status: Done
```

Now you can create command templates, use environment variables to configure your scripts, and set some values for those.
---
description: A simple tutorial on how to use the library to add exit handlers 
---

# Exit handlers

If you ever wanted to have some post orchestration steps that are run regardless of success of failure of the project
you can now define exit_handlers using the library.

## What is an exit handler ?

An exit_handler is a common step that will be called after your full orchestration ran. Independent to the results of
the steps, allowing you the capacity to do some clean up / reporting / any action required after a run.

## How to define an exit handler ?

By making use of the library, you can add a specific template folder called `on_exit`

Every template defined in this folder will be registered as an exit handler ensuring it will be ran after the
orchestration is finished.

## What do I need to know about those handlers ?

First ALL defined exit handlers will be run in alphabetical order, so if you have multiple library plugins adding
handlers ALL of those will be run.

Second they use the exact same syntax as any command template so you can define environment variables, arguments and
more.

But one environment variable is added to their list by csm-orc : `CSM_ORC_IS_SUCCESS` which is a boolean value set to
`True` if the orchestration was a success, and set to `False` if ANY step failed.

## Skipping exit handlers

In some situations you may want to run without executing the exit handlers (e.g. during local development or testing).
You can disable them with the `--no-exit-handlers` flag:

```bash title="Run without exit handlers"
csm-orc run my_template.json --no-exit-handlers
```

The same behaviour can be triggered via the `CSM_ORCHESTRATOR_USE_EXIT_HANDLERS` environment variable:

```bash title="Disable exit handlers via env var"
CSM_ORCHESTRATOR_USE_EXIT_HANDLERS=false csm-orc run my_template.json
```

Exit handlers are **enabled by default**. Pass `--exit-handlers` (or set the env var to `true`) to make the default explicit.
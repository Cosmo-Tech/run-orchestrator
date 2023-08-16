---
hide:
  - toc
---
# Orchestrator

!!! info "Help command"
    ```text
    --8<-- "generated/commands_help/csm-run-orchestrator_orchestrator.txt"
    ```

--8<-- "partials/orchestrator_known_issues.md"

## Examples

??? info "JSON Schema"
    ```json
    --8<-- "cosmotech/orchestrator/schema/run_template_json_schema.json"
    ```

??? example "Example json file"
    ```json title="simple_example.json"
    --8<-- "examples/simple.json"
    ```

??? note "Run command with json file"
    The following code won't run by itself because `example.json` requires the EnvVar `NO_EXIST` to be set by the system
    ```bash title="run without complementary EnvVar"
    csm-run-orchestrator orchestrator example.json
    ```
    You could do the following to have it work
    ```bash title="set EnvVar with export"
    export NO_EXIST="This value exists"
    csm-run-orchestrator orchestrator example.json
    ```
    The following works too
    ```bash title="run with EnvVar for run only"
    NO_EXIST="This value exists" csm-run-orchestrator orchestrator example.json
    ```
---
hide:
  - toc
description: "Command help: `csm-orc run-step`"
---
# Run Template Step

!!!danger "Depreciation Warning"
    **This command is deprecated since 1.5.2**  
    This command existed for migration purposes from Cosmo Tech API 2.4 to 3.0, 
    since API 4.0 is getting ready this command should not be required anymore.  
    ```json title="Equivalent to csm-orc run-step"
    {
        "command": "python"
        "arguments": [ "code/run_templates/my_template/my_step/main.py" ]
    }
    ```
    This command will be fully removed in a future version.

!!! info "Help command"
    ```text
    --8<-- "generated/commands_help/csm-orc_run-step.txt"
    ```
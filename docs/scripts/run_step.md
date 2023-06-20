---
hide:
  - toc
---
# Run Template Step

!!! info "Help command"
    ```text
    └▶ cosmotech_run_step --help
                                                                                                   
     Usage: cosmotech_run_step [OPTIONS] TEMPLATE [STEPS]...                                       
                                                                                                   
     Runs a list of steps of a run template in a CosmoTech project                                 
                                                                                                   
      • TEMPLATE refer to a folder contained in code/run_templates                                 
      • STEPS is a list of Steps definer in the TEMPLATE folder that will be executed              
         • defaults to CSMDOCKER which represent the legacy order: parameters_handler - validator  
           - prerun - engine - postrun                                                             
                                                                                                   
     Known limitations:                                                                            
                                                                                                   
      • The template MUST contain a main.py file with a main() function                            
      • The engine step requires to set the env var CSM_SIMULATION if you have a run without a     
        python engine                                                                              
                                                                                                   
    ╭─ Arguments ─────────────────────────────────────────────────────────────────────────────────╮
    │ *  TEMPLATE    TEXT  [required]                                                             │
    │    STEPS       TEXT                                                                         │
    ╰─────────────────────────────────────────────────────────────────────────────────────────────╯
    ╭─ Options ───────────────────────────────────────────────────────────────────────────────────╮
    │ --log-level    LVL  Either CRITICAL, ERROR, WARNING, INFO or DEBUG                          │
    │                     [env var: LOG_LEVEL]                                                    │
    │ --help              Show this message and exit.                                             │
    ╰─────────────────────────────────────────────────────────────────────────────────────────────╯
    ```
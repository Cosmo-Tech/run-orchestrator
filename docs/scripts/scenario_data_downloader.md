---
hide:
  - toc
---
# Scenario Data Download

!!! info "Help command"
    ```text
    └▶ cosmotech_scenario_downloader --help
                                                                                               
     Usage: cosmotech_scenario_downloader [OPTIONS]                                                
                                                                                                   
     Uses environment variables to call the download_scenario_data function Requires a valid Azure 
     connection either with:                                                                       
                                                                                                   
      • The AZ cli command: az login                                                               
      • A triplet of env var AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET                 
                                                                                                   
     Requires env var CSM_API_URL     The url to a cosmotech api                                   
     Requires env var CSM_API_SCOPE   The identification scope of a cosmotech api                  
                                                                                                   
    ╭─ Options ───────────────────────────────────────────────────────────────────────────────────╮
    │ *  --organization-id             o-##########  The id of an organization in the cosmotech   │
    │                                                api                                          │
    │                                                [env var: CSM_ORGANIZATION_ID]               │
    │                                                [required]                                   │
    │ *  --workspace-id                w-##########  The id of a workspace in the cosmotech api   │
    │                                                [env var: CSM_WORKSPACE_ID]                  │
    │                                                [required]                                   │
    │ *  --scenario-id                 s-##########  The id of a scenario in the cosmotech api    │
    │                                                [env var: CSM_SCENARIO_ID]                   │
    │                                                [required]                                   │
    │ *  --dataset-absolute-path       PATH          A local folder to store the main dataset     │
    │                                                content                                      │
    │                                                [env var: CSM_DATASET_ABSOLUTE_PATH]         │
    │                                                [required]                                   │
    │ *  --parameters-absolute-path    PATH          A local folder to store the parameters       │
    │                                                content                                      │
    │                                                [env var: CSM_PARAMETERS_ABSOLUTE_PATH]      │
    │                                                [required]                                   │
    │    --log-level                   LVL           Either CRITICAL, ERROR, WARNING, INFO or     │
    │                                                DEBUG                                        │
    │                                                [env var: LOG_LEVEL]                         │
    │    --help                                      Show this message and exit.                  │
    ╰─────────────────────────────────────────────────────────────────────────────────────────────╯
    ```
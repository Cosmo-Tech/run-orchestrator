---
hide:
  - toc
---
# Simulation to ADX connector

??? info "Help command"
    ```text
    └▶ cosmotech_simulation_to_adx_connector --help
    Usage: cosmotech_simulation_to_adx_connector [OPTIONS]                                                      
                                                                                                                 
    Uses environment variables to send content of CSV files to ADX Requires a valid Azure connection either     
    with:                                                                                                       
                                                                                                                
     • The AZ cli command: az login                                                                             
     • A triplet of env var AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET                               
                                                                                                                 
    ╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────╮
    │ *  --dataset-absolute-path                   PATH  A local folder to store the main dataset content       │
    │                                                    [env var: CSM_DATASET_ABSOLUTE_PATH]                   │
    │                                                    [required]                                             │
    │ *  --parameters-absolute-path                PATH  A local folder to store the parameters content         │
    │                                                    [env var: CSM_PARAMETERS_ABSOLUTE_PATH]                │
    │                                                    [required]                                             │
    │ *  --simulation-id                           UUID  the Simulation Id to add to records                    │
    │                                                    [env var: CSM_SIMULATION_ID]                           │
    │                                                    [required]                                             │
    │ *  --adx-uri                                 URI   the ADX cluster path (URI info can be found into ADX   │
    │                                                    cluster page)                                          │
    │                                                    [env var: AZURE_DATA_EXPLORER_RESOURCE_URI]            │
    │                                                    [required]                                             │
    │ *  --adx-ingest-uri                          URI   The ADX cluster ingest path (URI info can be found     │
    │                                                    into ADX cluster page)                                 │
    │                                                    [env var: AZURE_DATA_EXPLORER_RESOURCE_INGEST_URI]     │
    │                                                    [required]                                             │
    │ *  --database-name                           NAME  The targeted database name                             │
    │                                                    [env var: AZURE_DATA_EXPLORER_DATABASE_NAME]           │
    │                                                    [required]                                             │
    │    --send-parameters/--no-send-parameters          whether or not to send parameters (parameters path is  │
    │                                                    mandatory then)                                        │
    │                                                    [env var: CSM_SEND_DATAWAREHOUSE_PARAMETERS]           │
    │    --send-datasets/--no-send-datasets              whether or not to send datasets (parameters path is    │
    │                                                    mandatory then)                                        │
    │                                                    [env var: CSM_SEND_DATAWAREHOUSE_DATASETS]             │
    │    --wait/--no-wait                                Toggle waiting for the ingestion results               │
    │                                                    [env var: WAIT_FOR_INGESTION]                          │
    │    --log-level                               LVL   Either CRITICAL, ERROR, WARNING, INFO or DEBUG         │
    │                                                    [env var: LOG_LEVEL]                                   │
    │    --help                                          Show this message and exit.                            │
    ╰───────────────────────────────────────────────────────────────────────────────────────────────────────────╯
    ```

!!! notes "Env var list"
    | Environment variable | Parameter | Description |
    | ---- | ---- | ---- |
    | `CSM_DATASET_ABSOLUTE_PATH` | `--dataset-absolute-path` | A local folder to store the main dataset content |
    | `CSM_PARAMETERS_ABSOLUTE_PATH` | `--parameters-absolute-path` | A local folder to store the parameters content |
    | `CSM_SIMULATION_ID` | `--simulation-id` | the Simulation ID to add to records |
    | `AZURE_DATA_EXPLORER_RESOURCE_URI` | `--adx-uri` |  the ADX cluster path (URI info can be found into ADX cluster page) |
    | `AZURE_DATA_EXPLORER_RESOURCE_INGEST_URI` | `--adx-ingest-uri ` | The ADX cluster ingest path (URI info can be found into ADX cluster page) |
    | `AZURE_DATA_EXPLORER_DATABASE_NAME` | `--database-name` | The targeted database name |
    | `CSM_SEND_DATAWAREHOUSE_PARAMETERS` | `--send-parameters/--no-send-parameters` | whether to send parameters |
    | `CSM_SEND_DATAWAREHOUSE_DATASETS` | `--send-datasets/--no-send-datasets` | whether to send datasets |
    | `WAIT_FOR_INGESTION` | `--wait/--no-wait` | Toggle waiting for the ingestion results |
    | `LOG_LEVEL` | `--log-level` | Either CRITICAL, ERROR, WARNING, INFO or DEBUG |
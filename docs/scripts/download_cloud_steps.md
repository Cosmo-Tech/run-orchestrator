---
hide:
  - toc
---
# Download Steps from cloud

!!! info "Command help"
    ```text
    └▶ cosmotech_download_cloud_steps --help
                                                                                                   
     Usage: cosmotech_download_cloud_steps [OPTIONS]                                               
                                                                                                   
     Uses environment variables to download cloud based Template steps Requires a valid Azure      
     connection either with:                                                                       
                                                                                                   
      • The AZ cli command: az login                                                               
      • A triplet of env var AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET                 
                                                                                                   
    ╭─ Options ───────────────────────────────────────────────────────────────────────────────────╮
    │    --log-level          LVL                  Either CRITICAL, ERROR, WARNING, INFO or DEBUG │
    │                                              [env var: LOG_LEVEL]                           │
    │ *  --organization-id    o-##########         The id of an organization in the cosmotech api │
    │                                              [env var: CSM_ORGANIZATION_ID]                 │
    │                                              [required]                                     │
    │ *  --workspace-id       w-##########         The id of a solution in the cosmotech api      │
    │                                              [env var: CSM_WORKSPACE_ID]                    │
    │                                              [required]                                     │
    │ *  --run-template-id    NAME                 The name of the run template in the cosmotech  │
    │                                              api                                            │
    │                                              [env var: CSM_RUN_TEMPLATE_ID]                 │
    │                                              [required]                                     │
    │ *  --handler-list       HANDLER,...,HANDLER  A list of handlers to download (comma          │
    │                                              separated)                                     │
    │                                              [env var: CSM_CONTAINER_MODE]                  │
    │                                              [required]                                     │
    │ *  --api-url            URL                  The url to a Cosmotech API                     │
    │                                              [env var: CSM_API_URL]                         │
    │                                              [required]                                     │
    │ *  --api-scope          URI                  The identification scope of a Cosmotech API    │
    │                                              [env var: CSM_API_SCOPE]                       │
    │                                              [required]                                     │
    │    --help                                    Show this message and exit.                    │
    ╰─────────────────────────────────────────────────────────────────────────────────────────────╯
    ```
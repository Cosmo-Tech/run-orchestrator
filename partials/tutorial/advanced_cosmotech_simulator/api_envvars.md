| Environment Variable                    | Description |
| --------------------------------------- | ----------- |
| AZURE_CLIENT_ID                         | An identifier to an Azure identity defined during the installation of the platform
| AZURE_CLIENT_SECRET                     | A secret tied to the given client ID allowing to connect with it
| AZURE_TENANT_ID                         | An identifier of your Azure tenant to be able to connect to it
| IDENTITY_PROVIDER                       | Will be set to  `azure` in an Azure-based API
| CSM_API_URL                             | The URL to the Cosmo Tech API you are connecting to
| CSM_API_SCOPE                           | An identifier scope used to get permission to your API
| CSM_DATASET_ABSOLUTE_PATH               | A local folder path to which an external volume is mounted to and in which you can write datasets
| CSM_PARAMETERS_ABSOLUTE_PATH            | A local folder path to which an external volume is mounted to and in which you can write parameters
| CSM_RUN_TYPE                            | A parameter injected by the API into every Argo run, either `run` (default) or `delete`, used by csm-orc to launch either a `run.json` or `delete.json`
| TWIN_CACHE_HOST                         | The URL to the twin cache service inside the platform (deprecated)
| TWIN_CACHE_PORT                         | The port to the twin cache service inside the platform (deprecated)
| TWIN_CACHE_PASSWORD                     | The password to the twin cache service inside the platform (deprecated)
| TWIN_CACHE_USERNAME                     | The username to the twin cache service inside the platform (deprecated)
| CSM_SIMULATION_ID                       | The  `Simulation` ID for your current scenario run
| AZURE_DATA_EXPLORER_RESOURCE_URI        | The URI used to query an Azure Data Explorer Cluster tied to your  `Workspace`
| AZURE_DATA_EXPLORER_RESOURCE_INGEST_URI | The URI used to send data to an  `Azure Data Explorer` Cluster tied to your  `Workspace`
| AZURE_DATA_EXPLORER_DATABASE_NAME       | The name of the database of your  `Workspace` in  `Azure Data Explorer`
| CSM_ORGANIZATION_ID                     | The ID of your  `Organization` in the Cosmo Tech API
| CSM_WORKSPACE_ID                        | The ID of your  `Workspace` in the Cosmo Tech API
| CSM_SCENARIO_ID                         | The ID of your  `Scenario` in the Cosmo Tech API
| CSM_RUN_TEMPLATE_ID                     | The ID of your  `Run Template` in the Cosmo Tech API (as defined in your Solution)
| CSM_CONTAINER_MODE                      | Will always be `csm-orc` left for compatibility with pre 3.0 API
| CSM_ENTRYPOINT_LEGACY                   | Will always be  `false`
| CSM_PROBES_MEASURES_TOPIC               | An  `amqp` address used by the simulator to send your probe data to ADX via Event Hub
| CSM_CONTROL_PLANE_TOPIC                 | An  `amqp` address used by the simulator to send your control info to ADX via Event Hub (mostly number of measures sent)
| CSM_SIMULATION                          | The  `Simulation` file that should be used to run your simulation (this value is defined in your  `Run Template` and targets one of the files in the `Simulation/` folder)
"""
Pseudo code of kotlin version:
application() :
    csv_infos = map of path to csv_data
    if download_dataset :
        list_csv(path_to_dataset, csv_infos)
    if download_parameters:
        list_csv(path_to_parameters, csv_infos)
    process_csvs(csv_infos)

list_csv(path, csv_infos_storage):
    foreach csv in path:
        header = read header of csv
        mapping = foreach header.columns -> string
        csv_infos_storage add : csv.filepath -> csvdata (csv.filename, mapping)

process_csvs(csv_infos_storage):
    prepare_queries
    create_tables
    insert_data

create_tables() :
    construct_queries
    foreach query:
        execute query
        check if table created

prepare_queries(csv_infos):
    create_map = map of csv_file_path to header_infos

insert_data(csv_infos):
    create ingestion client
    foreach csv_file:
        open csv_file
        add column simulationRun to headers_infos
        create ingestion_mapping
        create ingestion_properties
        set ingestion_mapping and dropByTags
        ingest csv_file + ingestion_properties

construct_queries():
    queries : map table_name -> query
    foreach csv_file:
        table_name = csv_file.filename
        query = ".create-merge table " + table_name + "("
        query += ",".join(
            foreach field:
                field.name + ":" + field.type
        )
        query += ")"
        queries[table_name] = query
"""

"""
ENV VARS
- CSM_SEND_DATAWAREHOUSE_PARAMETERS: whether or not to send parameters (parameters path is mandatory then)
- CSM_SEND_DATAWAREHOUSE_DATASETS: whether or not to send datasets (datasets path is mandatory then)
- CSM_DATASET_ABSOLUTE_PATH: The dataset absolute path
- CSM_PARAMETERS_ABSOLUTE_PATH: The parameters absolute path
- AZURE_DATA_EXPLORER_RESOURCE_INGEST_URI : the ADX cluster ingest path (URI info can be found into ADX cluster page)
- AZURE_DATA_EXPLORER_RESOURCE_URI : the ADX cluster path (URI info can be found into ADX cluster page)
- AZURE_TENANT_ID : the Azure Tenant id (can be found under the App registration screen)
- AZURE_CLIENT_ID : the Azure client id (can be found under the App registration screen)
- AZURE_CLIENT_SECRET: the Azure client secret (can be found under the App registration screen)
- CSM_SIMULATION_ID: the Simulation Id to add to records (direct mode only)
- AZURE_DATA_EXPLORER_DATABASE_NAME : the targeted database name
"""
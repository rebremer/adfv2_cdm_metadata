# Azure Data Factory pipeline that does the following:

- Get process metadata from blob storage (data owner, data source, privacy level, classification)
- Get technical metadata from tables in SQLDB (schema name, tablename, fieldname, field type)
- Copy tables from SQLDB to ADLS gen 2 where every table is a File System with the following folder structure: Table_name/yyyy/MM/dd
- Add process metadata, technical metadata and processing metadate in a model.json file to the folder structure for each dataset. Model.json is compliant to the Common Data Model (cdm) jsonschema. An Azure Function in Python is used for this, ADFv2 pipeline is depicted as follows:

Base pipeline:

![Base pipeline](https://github.com/rebremer/adfv2_cdm_metadata/blob/master/adfv2pipelineimages/basepipeline.png)

Copy and metadata pipeline including Azure Function in Python:

![Copy_metadata pipeline](https://github.com/rebremer/adfv2_cdm_metadata/blob/master/adfv2pipelineimages/copy_cdm_pipeline.png)


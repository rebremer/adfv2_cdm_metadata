### Azure Data Factory (ADFv2) copy & metadata pipeline using common data model (CDM) syntax ###

The following steps are executed:

- Get process metadata from blob storage (data owner, data source, privacy level, classification)
- Get technical metadata from tables in SQLDB (schema name, tablename, fieldname, field type)
- Copy tables from SQLDB to ADLS gen 2 where every table is a File System with the following folder structure: Table_name/yyyy/MM/dd
- Add process metadata, technical metadata and post processing metadata (timestamp) in a model.json file to the folder structure for each dataset. Model.json is compliant to the Common Data Model (cdm) jsonschema. An Azure Function in Python is used for this, ADFv2 pipeline is depicted as follows:

#### Base pipeline: ####

![Base pipeline](https://github.com/rebremer/adfv2_cdm_metadata/blob/master/adfv2pipelineimages/basepipeline.png)

#### Copy and metadata pipeline including Azure Function in Python: ####

![Copy_metadata pipeline](https://github.com/rebremer/adfv2_cdm_metadata/blob/master/adfv2pipelineimages/copy_cdm_pipeline.png)

#### Data and model.json metadata in ADLS gen2 Filesystem: ####

![Data and model.json](https://github.com/rebremer/adfv2_cdm_metadata/blob/master/adfv2pipelineimages/data_medata_adlsgen2.png)

#### Content of model.json ####

```json
{
    "name": "OrdersProductsV3",
    "description": "",
    "version": "1.0",
    "annotation": {
        "retentionPeriod": 62,
        "sourceSystem": "DIH",
        "IngestionDate": "2019-09-09 16:56:00Z",
        "privacyLevel": "222"
    },
    "entities": [
        {
            "$type": "LocalEntity",
            "name": "SalesLTProductCategory",
            "description": "",
            "attributes": [
                {
                    "name": "CustomerID",
                    "dataType": "int64"
                },
                {
                    "name": "NameStyle",
                    "dataType": "boolean"
                },
                {
                    "name": "Title",
                    "dataType": "string"
                },
                {
                    "name": "FirstName",
                    "dataType": "string"
                },
                {
                    "name": "MiddleName",
                    "dataType": "string"
                },
                {
                    "name": "LastName",
                    "dataType": "string"
                },
                {
                    "name": "Suffix",
                    "dataType": "string"
                },
                {
                    "name": "CompanyName",
                    "dataType": "string"
                },
                {
                    "name": "SalesPerson",
                    "dataType": "string"
                },
                {
                    "name": "EmailAddress",
                    "dataType": "string"
                },
                {
                    "name": "Phone",
                    "dataType": "string"
                },
                {
                    "name": "PasswordHash",
                    "dataType": "string"
                },
                {
                    "name": "PasswordSalt",
                    "dataType": "string"
                },
                {
                    "name": "rowguid",
                    "dataType": "guid"
                },
                {
                    "name": "ModifiedDate",
                    "dataType": "dateTime"
                }
            ]
        }
    ]
}
```
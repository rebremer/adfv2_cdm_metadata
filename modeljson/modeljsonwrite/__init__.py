import logging
import os
#import uuid
from adal import AuthenticationContext
from azure.storage.blob import (
    AppendBlobService,
    BlockBlobService,
    BlobPermissions,
    ContainerPermissions
)
from azure.storage.common import (
    TokenCredential
)
import azure.functions as func
from msrestazure.azure_active_directory import MSIAuthentication
from jsonschema import validate
import collections
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    logging.info(req.get_body())
    inputreq = json.loads(req.get_body())

    par_tableStructureArray = inputreq['tableStructureArray']
    par_tableNameArray = inputreq['tableNameArray']
    par_ADLSgen2stor = inputreq['ADLSgen2stor']
    par_filepath = inputreq['filepath']
    par_processMetaDataStor = inputreq['processMetaDataStor']
    #par_processMetaData = json.loads(req.params.get('par_processMetaData'))

    d = collections.OrderedDict()

    # set header
    d['name'] = "BlogMetaData"
    d['description'] = "Example model.json using CDM json schema"
    d['version'] = "1.0"
    annotation = collections.OrderedDict()
    annotation['retentionPeriod'] = par_processMetaDataStor[0]['firstRow']['retentionPeriod']
    annotation['sourceSystem'] = par_processMetaDataStor[0]['firstRow']['sourceSystem']
    annotation['IngestionDate'] = par_processMetaDataStor[0]['firstRow']['generationData']
    annotation['privacyLevel'] = par_processMetaDataStor[0]['firstRow']['privacyLevel']
    d['annotation'] = annotation

    # set entities
    entities = []
    i=0
    while i < len(par_tableStructureArray):
        #print ("TABLE: " + par_tableNameArray[i])
  
        tableStructure = par_tableStructureArray[i]['structure']
        array = []
        for field in tableStructure:
            #print(field['name'] + ', ' + field['physicalType'])
            if field['logicalType'] == "Int32" or field['logicalType'] == "Byte" or field['logicalType'] == "Int16":
                array.append({"name": field['name'], "dataType": "int64"})
            elif field['logicalType'] == "String":
                array.append({"name": field['name'], "dataType": "string"})
            elif field['logicalType'] == "Guid":
                array.append({"name": field['name'], "dataType": "guid"})
            elif field['logicalType'] == "DateTime":
                array.append({"name": field['name'], "dataType": "dateTime"})
            elif field['logicalType'] == "Boolean":
                array.append({"name": field['name'], "dataType": "boolean"})
            elif field['logicalType'] == "Decimal":
                array.append({"name": field['name'], "dataType": "decimal"})
            elif field['logicalType'] == "Byte[]":
                array.append({"name": field['name'], "dataType": "unclassified"})
            else:
                array.append({"name": field['name'], "dataType": field['logicalType']})
          
        entities.append({"$type": "LocalEntity", "name": par_tableNameArray[i], "description": "", "attributes": array})
    
        i+=1
        #print("\n")

    d['entities'] = entities

    model_json = json.dumps(d, indent=4)
    model_json_string = json.loads(model_json)
    schema_file=loadSchema()
    validate(instance=model_json_string, schema=schema_file)
    
    credentials = MSIAuthentication(resource='https://storage.azure.com/')    
    blob_service = BlockBlobService(par_ADLSgen2stor, token_credential=credentials)
 
    blob_service.create_blob_from_text(par_filepath[0:par_filepath.find("/")], par_filepath[par_filepath.find("/")+1:] + "/model.json", model_json)
    result = {"status": "ok"}

    return func.HttpResponse(str(result))


def loadSchema():

    schema={
      "definitions": {
        "annotation": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 256,
                    "pattern": "^[^\\s](.*[^\\s])?$"
                },
                "value": {
                    "type": "string"
                }
            },
            "required": [
                "name"
            ]
        },
        "referenceModel": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "string"
                },
                "location": {
                    "type": "string",
                    "format": "uri"
                }
            },
            "required": [
                "id",
                "location"
            ]
        },
        "entity": {
            "type": "object",
            "properties": {
                "$type": {
                    "type": "string",
                    "enum": [
                        "LocalEntity",
                        "ReferenceEntity"
                    ]
                },
                "name": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 256,
                    "pattern": "^[^\\s]([^.\"]*[^\\s])?$"
                },
                "description": {
                    "type": "string",
                    "maxLength": 4000
                },
                "annotations": {
                    "type": "array",
                    "items": {
                        "$ref": "#/definitions/annotation"
                    }
                },
                "isHidden": {
                    "$ref": "#/definitions/isHidden"
                }
            },
            "required": [
                "$type",
                "name"
            ]
        },
        "localEntity": {
            "allOf": [
                {
                    "$ref": "#/definitions/entity"
                },
                {
                    "properties": {
                        "$type": {
                            "type": "string",
                            "const": "LocalEntity"
                        },
                        "attributes": {
                            "$id": "#/properties/entities/items/properties/attributes",
                            "type": "array",
                            "items": {
                                "$ref": "#/definitions/attribute"
                            }
                        },
                        "partitions": {
                            "$id": "#/properties/entities/items/properties/partitions",
                            "type": "array",
                            "items": {
                                "$ref": "#/definitions/partition"
                            }
                        },
                        "schemas": {
                            "$id": "#/properties/entities/items/properties/schemas",
                            "type": "array",
                            "items": {
                                "$id": "#/properties/entities/items/properties/schemas/items",
                                "type": "string",
                                "pattern": "^https://raw\\.githubusercontent\\.com/Microsoft/CDM/master/schemaDocuments/core/([a-zA-Z]+/?)*[a-zA-Z0-9.]+\\.[0-9.]+\\.cdm\\.json$",
                                "examples": [
                                    "https://raw.githubusercontent.com/Microsoft/CDM/master/schemaDocuments/core/applicationCommon/foundationCommon/Product.0.7.cdm.json",
                                    "https://raw.githubusercontent.com/Microsoft/CDM/master/schemaDocuments/core/applicationCommon/foundationCommon/crmCommon/accelerators/healthCare/electronicMedicalRecords/Product.0.7.cdm.json"
                                ]
                            }
                        }
                    },
                    "required": [
                        "$type",
                        "attributes"
                    ]
                }
            ]
        },
        "referenceEntity": {
            "allOf": [
                {
                    "$ref": "#/definitions/entity"
                },
                {
                    "properties": {
                        "$type": {
                            "type": "string",
                            "const": "ReferenceEntity"
                        },
                        "source": {
                            "type": "string"
                        },
                        "modelId": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "$type",
                        "source",
                        "modelId"
                    ]
                }
            ]
        },
        "attribute": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 256,
                    "pattern": "^[^\\s](.*[^\\s])?$"
                },
                "description": {
                    "type": "string",
                    "maxLength": 4000
                },
                "dataType": {
                    "type": "string",
                    "enum": [
                        "unclassified",
                        "string",
                        "int64",
                        "double",
                        "dateTime",
                        "dateTimeOffset",
                        "decimal",
                        "boolean",
                        "guid",
                        "json"
                    ]
                },
                "annotations": {
                    "type": "array",
                    "items": {
                        "$ref": "#/definitions/annotation"
                    }
                }
            },
            "required": [
                "name",
                "dataType"
            ]
        },
        "partition": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 256,
                    "pattern": "^[^\\s](.*[^\\s])?$"
                },
                "description": {
                    "type": "string",
                    "maxLength": 4000
                },
                "refreshTime": {
                    "type": "string"
                },
                "location": {
                    "type": "string",
                    "format": "uri"
                },
                "fileFormatSettings": {
                    "$ref": "#/definitions/fileFormatSettings"
                },
                "isHidden": {
                    "$ref": "#/definitions/isHidden"
                }
            },
            "required": [
                "name"
            ]
        },
        "isHidden": {
            "type": "boolean"
        },
        "fileFormatSettings": {
            "oneOf": [
                {
                    "$ref": "#/definitions/CsvFormatSettings"
                }
            ],
            "required": [
                "$type"
            ]
        },
        "CsvFormatSettings": {
            "type": "object",
            "properties": {
                "$type": {
                    "type": "string",
                    "const": "CsvFormatSettings"
                },
                "columnHeaders": {
                    "type": "boolean",
                    "default": "false"
                },
                "delimiter": {
                    "type": "string",
                    "default": ","
                },
                "quoteStyle": {
                    "type": "string",
                    "enum": [
                        "QuoteStyle.Csv",
                        "QuoteStyle.None"
                    ],
                    "default": "QuoteStyle.Csv"
                },
                "csvStyle": {
                    "type": "string",
                    "enum": [
                        "CsvStyle.QuoteAlways",
                        "CsvStyle.QuoteAfterDelimiter"
                    ],
                    "default": "CsvStyle.QuoteAlways"
                }
            },
            "required": [
                "$type"
            ]
        },
        "SingleKeyRelationship": {
            "type": "object",
            "properties": {
                "$type": {
                    "type": "string",
                    "const": "SingleKeyRelationship"
                },
                "fromAttribute": {
                    "$ref": "#/definitions/referenceAttribute"
                },
                "toAttribute": {
                    "$ref": "#/definitions/referenceAttribute"
                }
            },
            "required": [
                "$type",
                "fromAttribute",
                "toAttribute"
            ]
        },
        "referenceAttribute": {
            "type": "object",
            "properties": {
                "entityName": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 1024,
                    "pattern": "^[^\\s](.*[^\\s])?$"
                },
                "attributeName": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 256,
                    "pattern": "^[^\\s](.*[^\\s])?$"
                }
            },
            "required": [
                "entityName",
                "attributeName"
            ]
        }
    },
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "http://example.com/root.json",
    "type": "object",
    "title": "The Root Schema",
    "required": [
        "name",
        "version",
        "entities"
    ],
    "properties": {
        "application": {
            "$id": "#/properties/application",
            "type": "string"
        },
        "name": {
            "$id": "#/properties/name",
            "type": "string",
            "minLength": 1,
            "maxLength": 256,
            "pattern": "^[^\\s](.*[^\\s])?$"
        },
        "description": {
            "$id": "#/properties/description",
            "type": "string",
            "maxLength": 4000
        },
        "version": {
            "$id": "#/properties/version",
            "type": "string",
            "enum": [
                "1.0"
            ]
        },
        "culture": {
            "$id": "#/properties/culture",
            "type": "string"
        },
        "modifiedTime": {
            "$id": "#/properties/modifiedTime",
            "type": "string"
        },
        "isHidden": {
            "$id": "#/properties/isHidden",
            "$ref": "#/definitions/isHidden"
        },
        "annotations": {
            "$id": "#/properties/annotations",
            "type": "array",
            "items": {
                "$ref": "#/definitions/annotation"
            }
        },
        "entities": {
            "$id": "#/properties/entities",
            "type": "array",
            "items": {
                "oneOf": [
                    {
                        "$ref": "#/definitions/localEntity"
                    },
                    {
                        "$ref": "#/definitions/referenceEntity"
                    }
                ]
            }
        },
        "referenceModels": {
            "$id": "#/properties/referenceModels",
            "type": "array",
            "items": {
                "$ref": "#/definitions/referenceModel"
            }
        },
        "relationships": {
            "$id": "#/properties/relationships",
            "type": "array",
            "items": {
                "oneOf": [
                    {
                        "$ref": "#/definitions/SingleKeyRelationship"
                    }
                ]
            }
        }
      }
    }
    return schema
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
from . import cdmschema
from datetime import datetime
writeToStor = False

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
    d['modifiedTime'] = str(datetime.utcnow().isoformat()) + "Z"
    annotation = collections.OrderedDict()
    annotation['retentionPeriod'] = par_processMetaDataStor[0]['firstRow']['retentionPeriod']
    annotation['sourceSystem'] = par_processMetaDataStor[0]['firstRow']['sourceSystem']
    annotation['IngestionDate'] = par_processMetaDataStor[0]['firstRow']['generationData']
    annotation['privacyLevel'] = par_processMetaDataStor[0]['firstRow']['privacyLevel']
    d['annotation'] = annotation

    # set entities
    entities = []
    array = []
    for field in par_tableStructureArray:
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
          
    entities.append({"$type": "LocalEntity", "name": par_tableNameArray, "description": "", "attributes": array})
    d['entities'] = entities

    model_json = json.dumps(d, indent=4)
    
    model_json_string = json.loads(model_json)
    schema_file=cdmschema.loadSchema()
    validate(instance=model_json_string, schema=schema_file)
    
    if writeToStor == True:
        credentials = MSIAuthentication(resource='https://storage.azure.com/')    
        blob_service = BlockBlobService(par_ADLSgen2stor, token_credential=credentials)
        blob_service.create_blob_from_text(par_filepath[0:par_filepath.find("/")], par_filepath[par_filepath.find("/")+1:] + "/model.json", model_json)
        result = {"status": "ok"}
    else:
        result = model_json

    logging.info(str(result))
    return func.HttpResponse(str(result))
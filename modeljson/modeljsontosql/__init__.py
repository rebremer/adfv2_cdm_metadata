import logging

import azure.functions as func

import collections
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    logging.info(req.get_body())
    inputreq = json.loads(req.get_body())

    par_entities = inputreq['firstRow']['entities'][0]
    attributies = par_entities['attributes']

    tableStructure = []
    query = "CREATE TABLE " + "[" + par_entities['name'] + "]" + " ("
    datafileLocations = []
    for attribute in attributies:

        if attribute['dataType'] == "int64":
            datatype = "int"
        elif attribute['dataType'] == "string":
            datatype = "nvarchar(350)"
        elif attribute['dataType'] == "guid":
            datatype = "uniqueidentifier"
        elif attribute['dataType'] == "dateTime":
            datatype = "datetime"
        elif attribute['dataType'] == "boolean":
            datatype = "bit"
        elif attribute['dataType'] == "decimal":
            datatype = "float"
        elif attribute['dataType'] == "unclassified":
            attribute['dataType'] = "Byte[]"
            datatype = "varbinary(max)"          
        else:
            datatype = "nvarchar(350)"

        query += "[" + attribute['name'] + "] " + datatype + ","
        tableStructure.append({"name": attribute['name'], "type": attribute['dataType'], "typeSQL": datatype})

    query = query[:-1]   
    query += ")"


    results = []
    results.append({"name": par_entities['name'], "tableName": "[" + par_entities['name'] + "]", "modifiedTime": "null", "tableStructure": tableStructure, "query": query, "datafileLocations": datafileLocations})

    d = collections.OrderedDict() 
    d['results'] = results

    model_json = json.dumps(d, indent=4)
    logging.info(str(model_json))

    return func.HttpResponse(str(model_json))
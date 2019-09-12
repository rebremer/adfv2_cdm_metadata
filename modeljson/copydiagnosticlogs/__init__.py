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

from msrestazure.azure_active_directory import MSIAuthentication

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    logging.info(req.get_body())
    inputreq = json.loads(req.get_body())

    from_storage_account = inputreq['fromStorage'] # "testedlstorgen"
    to_storage_account =  inputreq['toStorage'] # "testedlloggingstor"
    to_storage_account_container = inputreq['toContainer'] # "diagnosticslogs"

    # In case you cannot use MSI (e.g. when you run this script on a local pc, you can create credentials using an SPN)
    #RESOURCE = "https://storage.azure.com/"
    #CLIENT_ID = "<your client id>"
    #CLIENT_SECRET = "<your client secret>"
    #TENANT_ID = "<your tenant id>"
    #AUTHORITY_URL = "https://login.microsoftonline.com/" + TENANT_ID

    #context = AuthenticationContext(AUTHORITY_URL)
    #token = context.acquire_token_with_client_credentials(
    #    RESOURCE,
    #    CLIENT_ID,
    #    CLIENT_SECRET)
    #credentials = TokenCredential(token["accessToken"]) 

    # MSI
    credentials = MSIAuthentication(resource='https://storage.azure.com/')
    blob_service_from = BlockBlobService(from_storage_account, token_credential=credentials)
    blob_service_to = BlockBlobService(account_name=to_storage_account, token_credential=credentials)

    generator = blob_service_from.list_blobs("$logs")
    for blob in generator:
        if blob.name[-4:] == ".log":
            #logging.info("\t Blob name: " + blob.name[:-4])
            input_blob = blob_service_from.get_blob_to_text("$logs", blob.name)
            blob_service_to.create_blob_from_text(to_storage_account_container, blob.name, str(input_blob))

    result = {"status": "ok"}
    return func.HttpResponse(str(result))
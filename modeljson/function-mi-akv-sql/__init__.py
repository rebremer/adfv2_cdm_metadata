import logging

import azure.functions as func
from msrestazure.azure_active_directory import MSIAuthentication
from azure.keyvault import KeyVaultClient
import pyodbc

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # set variables (todo: make environment variables of this)
    server  = "<<your logical sql sever name>>.database.windows.net"
    database = "<<your sqldb name>>"
    username = "<<your sqldb user name>>"
    secretname = "<<your secretname in you key vault>>"
    keyvaultname = "https://<<your key vault name>>.vault.azure.net/"

    # get secrets from key vault
    credentials = MSIAuthentication(resource='https://vault.azure.net')
    kvclient = KeyVaultClient(credentials)
    password = kvclient.get_secret(keyvaultname, secretname, "").value

    # Make connection to database
    connectionstring = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password
    logging.info(connectionstring)
    cnxn = pyodbc.connect(connectionstring)
    cursor = cnxn.cursor()

    # fire query
    cursor.execute("SELECT @@version;") 
    row = cursor.fetchone() 
    logging.info((row[0]))

    return func.HttpResponse(str(row[0]))
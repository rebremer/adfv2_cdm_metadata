import uuid
import adal
import pyodbc
import struct
from io import BytesIO

#using AAD for authentication
RESOURCE = "https://database.windows.net/"
CLIENT_ID = "<<my client id>>"
CLIENT_SECRET = "<<my secret>>"
TENANT_ID = "<<my tenant id>>"
AUTHORITY_URL = "https://login.microsoftonline.com/" + TENANT_ID

# CREATE USER [CLIENT_ID] FROM EXTERNAL PROVIDER;
# EXEC sp_addrolemember [db_datareader], [CLIENT_ID]
   
def run():

    context = adal.AuthenticationContext(AUTHORITY_URL)
    token = context.acquire_token_with_client_credentials(
        RESOURCE,
        CLIENT_ID,
        CLIENT_SECRET)
    token = token["accessToken"].encode()
    print (token)

    exptoken = b""
    for i in token:
        exptoken += bytes({i})
        exptoken += bytes(1)
    server  = '<<my sql server name>>.database.windows.net'
    database = '<<my database>>'
    connstr = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database
    tokenstruct = struct.pack("=i", len(exptoken)) + exptoken
    conn = pyodbc.connect(connstr, attrs_before = { 1256:tokenstruct })
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM SalesLT.Address")
    for row in cursor.fetchall():
        print (row)

    print ("done")

if __name__ == '__main__':
    run()

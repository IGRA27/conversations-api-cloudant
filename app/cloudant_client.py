from dotenv import load_dotenv
load_dotenv()                     # Carga las vars de .env en os.environ

import os
from cloudant import Cloudant

#Lee variables de entorno
CLOUDANT_URL      = os.getenv("CLOUDANT_URL")
CLOUDANT_API_KEY  = os.getenv("CLOUDANT_API_KEY")
CLOUDANT_DB_NAME  = os.getenv("CLOUDANT_DB_NAME", "conversations")

#Para Cloudant.iam necesitamos el account_name:
#ej: si URL="https://abc123.cloudantnosqldb.appdomain.cloud"
#entonces account_name="abc123"
account_name = CLOUDANT_URL.split("//")[1].split(".")[0]

#Inicializa cliente y base de datos
client = Cloudant.iam(
    account_name=account_name,
    api_key=CLOUDANT_API_KEY,
    connect=True
)
db = client.create_database(CLOUDANT_DB_NAME, throw_on_exists=False)

from cloudant import Cloudant
import os

#Lee variables de entorno:
CLOUDANT_URL      = os.getenv("CLOUDANT_URL")
CLOUDANT_API_KEY  = os.getenv("CLOUDANT_API_KEY")
CLOUDANT_DB_NAME  = os.getenv("CLOUDANT_DB_NAME", "conversations")

#Inicializa cliente
client = Cloudant.iam(
    account_name = CLOUDANT_URL.split("//")[1].split(".")[0],
    api_key      = CLOUDANT_API_KEY,
    connect=True
)

#Obtiene (o crea, para este caso ya esta creado en el dashboard, pero se puede comprobar) la base de datos
db = client.create_database(CLOUDANT_DB_NAME, throw_on_exists=False)

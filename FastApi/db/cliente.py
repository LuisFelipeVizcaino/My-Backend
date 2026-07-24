from pymongo import MongoClient
import os
import certifi
from dotenv import  load_dotenv

load_dotenv()

cliente = MongoClient(
    os.getenv("MONGO_URI"),
    tlsCAFile=certifi.where()
)

db_client = cliente.Pybackend

print("Conectando a MongoDB Atlas...")
print(cliente.admin.command("ping"))
print("Conexión exitosa")
import os
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "mutuelle_sahi"
DB_USER = "postgres"
DB_PASS = "0323"  # Votre mot de passe en chaîne de caractères

def get_engine():
    # Construction sécurisée de l'URL avec le driver pg8000 (100% Python)
    connection_url = URL.create(
        drivername="postgresql+pg8000",
        username=DB_USER,
        password=str(DB_PASS),
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME
    )
    
    return create_engine(connection_url)
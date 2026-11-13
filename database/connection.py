import os
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

# Configuration locale par défaut (utilisée si DATABASE_URL n'est pas défini)
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "mutuelle_sahi"
DB_USER = "postgres"
DB_PASS = "0323"  # Votre mot de passe

def get_engine():
    # Vérifier si une variable d'environnement DATABASE_URL existe (ex: sur Streamlit Cloud avec Neon)
    database_url = os.getenv("DATABASE_URL")
    
    if database_url:
        # S'assurer que SQLAlchemy utilise bien le driver pg8000
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql+pg8000://", 1)
        elif database_url.startswith("postgresql://") and "+pg8000" not in database_url:
            database_url = database_url.replace("postgresql://", "postgresql+pg8000://", 1)
            
        # Nettoyer les paramètres incompatibles avec pg8000 (ex: channel_binding)
        parsed_url = urlparse(database_url)
        query_params = parse_qs(parsed_url.query, keep_blank_values=True)
        
        if 'channel_binding' in query_params:
            del query_params['channel_binding']
            
        new_query = urlencode(query_params, doseq=True)
        database_url = urlunparse((
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            new_query,
            parsed_url.fragment
        ))
        
        return create_engine(database_url)
    
    # Fallback : Connexion locale avec URL.create si aucune variable d'environnement n'est détectée
    connection_url = URL.create(
        drivername="postgresql+pg8000",
        username=DB_USER,
        password=str(DB_PASS),
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME
    )
    
    return create_engine(connection_url)
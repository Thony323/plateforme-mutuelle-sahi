import os
from sqlalchemy import create_engine
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

def get_engine():
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        # Configuration locale de secours
        database_url = "postgresql://postgres:0323@localhost:5432/mutuelle_sahi"
    
    # Correction du protocole si nécessaire
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
        
    # Nettoyage des paramètres non pris en charge par psycopg2 (comme channel_binding)
    parsed_url = urlparse(database_url)
    query_params = parse_qs(parsed_url.query, keep_blank_values=True)
    
    # Supprimer channel_binding s'il est présent
    if 'channel_binding' in query_params:
        del query_params['channel_binding']
        
    # S'assurer que sslmode est bien défini à 'require' pour Neon
    if 'sslmode' not in query_params:
        query_params['sslmode'] = ['require']
        
    new_query = urlencode(query_params, doseq=True)
    clean_url = urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        parsed_url.params,
        new_query,
        parsed_url.fragment
    ))
    
    return create_engine(clean_url)
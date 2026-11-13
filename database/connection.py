import os
from sqlalchemy import create_engine

def get_engine():
    # Récupère l'URL de Neon (sur Streamlit Cloud) ou utilise le fallback local
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        # Configuration locale par défaut si DATABASE_URL n'est pas défini
        database_url = "postgresql://postgres:0323@localhost:5432/mutuelle_sahi"
    
    # Correction automatique si l'URL commence par postgres:// (ancien format)
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
        
    return create_engine(database_url)
from connection import get_engine
from sqlalchemy import text

def init_db():
    engine = get_engine()
    with open("database/schema.sql", "r", encoding="utf-8") as f:
        sql_schema = f.read()
    
    with engine.connect() as conn:
        conn.execute(text(sql_schema))
        conn.commit()
    print("✅ Base de données 'mutuelle_sahi' et tables créées avec succès !")

if __name__ == "__main__":
    init_db()
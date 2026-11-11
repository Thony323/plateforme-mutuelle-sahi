import os
import re
import urllib.parse
import pandas as pd
from sqlalchemy import create_engine, text

# Configuration de la base de données PostgreSQL
DB_USER = "postgres"
DB_PASSWORD = "0323"  # ⚠️ Remplacez si nécessaire
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "mutuelle_sahi"

PROCESSED_DIR = "data/processed"


def clean_column_name(col_name: str) -> str:
    """Normalise les noms de colonnes au format PostgreSQL (snake_case sans accents)."""
    c = str(col_name).strip().lower()
    replacements = {
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'à': 'a', 'â': 'a', 'ä': 'a',
        'î': 'i', 'ï': 'i',
        'ô': 'o', 'ö': 'o',
        'ù': 'u', 'û': 'u', 'ü': 'u',
        'ç': 'c', '%': 'pct', "'": '_', ' ': '_'
    }
    for orig, repl in replacements.items():
        c = c.replace(orig, repl)

    c = re.sub(r'[^a-z0-9_]', '_', c)
    c = re.sub(r'_+', '_', c).strip('_')
    return c


def load_data_to_postgres():
    user_encoded = urllib.parse.quote_plus(DB_USER)
    pass_encoded = urllib.parse.quote_plus(DB_PASSWORD)

    connection_string = f"postgresql://{user_encoded}:{pass_encoded}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(connection_string)

    print("=" * 80)
    print("🚀 INITIALISATION DU CHARGEMENT EN BASE POSTGRESQL")
    print("=" * 80)

    # 1. Suppression forcée des tables existantes avec CASCADE pour débloquer les contraintes
    tables_to_drop = [
        "fact_recu_sinistre", "fact_sinistre", "fact_recette",
        "fact_cotisation", "dim_contrat_membre", "dim_membre", "dim_contrat"
    ]

    print("🧹 Nettoyage des anciennes tables et contraintes...")
    with engine.connect() as conn:
        for tbl in tables_to_drop:
            conn.execute(text(f"DROP TABLE IF EXISTS {tbl} CASCADE;"))
        conn.commit()
    print("✅ Tables et contraintes précédentes supprimées avec succès !")

    # 2. Chargement des nouveaux fichiers CSV
    files_to_tables = [
        ("dim_contrat.csv", "dim_contrat"),
        ("dim_membre.csv", "dim_membre"),
        ("dim_contrat_membre.csv", "dim_contrat_membre"),
        ("fact_cotisation.csv", "fact_cotisation"),
        ("fact_recette.csv", "fact_recette"),
        ("fact_sinistre.csv", "fact_sinistre"),
        ("fact_recu_sinistre.csv", "fact_recu_sinistre")
    ]

    for csv_file, table_name in files_to_tables:
        file_path = os.path.join(PROCESSED_DIR, csv_file)

        if not os.path.exists(file_path):
            file_path = csv_file

        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path, low_memory=False)

                # Nettoyage des noms de colonnes
                df.columns = [clean_column_name(col) for col in df.columns]

                # Conversion automatique des dates
                for col in df.columns:
                    if 'date' in col:
                        df[col] = pd.to_datetime(df[col], errors='coerce')

                # Reconstitution de la table
                df.to_sql(
                    name=table_name,
                    con=engine,
                    if_exists='replace',
                    index=False,
                    chunksize=1000,
                    method='multi'
                )
                print(f"📥 {csv_file:<25} ➡️ Table '{table_name}': {len(df):,} lignes insérées.")

            except Exception as e:
                print(f"❌ Erreur lors du chargement de {csv_file}: {e}")
        else:
            print(f"⚠️ Fichier introuvable : {csv_file}")

    print("\n" + "=" * 80)
    print("🎉 CHARGEMENT TERMINÉ AVEC SUCCÈS ! LA BASE EST PRÊTE.")
    print("=" * 80)


if __name__ == "__main__":
    load_data_to_postgres()
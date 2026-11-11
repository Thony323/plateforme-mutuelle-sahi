import sys
from pathlib import Path
import pandas as pd
from sqlalchemy import text

# Résolution du chemin racine
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from database.connection import get_engine

def mettre_a_jour_type_prise_en_charge():
    # 1. Charger le fichier CSV nettoyé
    csv_path = ROOT_DIR / "data" / "processed" / "sinistres_recu_clean.csv"
    if not csv_path.exists():
        csv_path = Path("sinistres_recu_clean.csv")
        
    print("📖 Lecture du fichier nettoyé...")
    df_clean = pd.read_csv(csv_path)

    engine = get_engine()

    with engine.begin() as conn:
        # 2. Ajouter la colonne type_prise_en_charge si elle n'existe pas encore
        print("⚙️ Ajout de la colonne 'type_prise_en_charge' dans PostgreSQL...")
        conn.execute(text("""
            ALTER TABLE fact_sinistre 
            ADD COLUMN IF NOT EXISTS type_prise_en_charge VARCHAR(255);
        """))

        # 3. Mettre à jour la table PostgreSQL avec les valeurs du CSV
        print("🔄 Mise à jour des données dans PostgreSQL...")
        for _, row in df_clean.iterrows():
            sinistre_id = str(row['Sinistre']).strip()
            type_pec = str(row['Type de prise en charge']).strip()
            
            conn.execute(
                text("""
                    UPDATE fact_sinistre 
                    SET type_prise_en_charge = :type_pec 
                    WHERE sinistre_id = :sinistre_id;
                """),
                {"type_pec": type_pec, "sinistre_id": sinistre_id}
            )

    print("✅ Mise à jour terminée avec succès dans PostgreSQL !")

if __name__ == "__main__":
    mettre_a_jour_type_prise_en_charge()
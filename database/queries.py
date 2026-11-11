import sys
from pathlib import Path

# Fix pour permettre l'import de 'database.connection' peu importe d'où est lancé le fichier
sys.path.append(str(Path(__file__).resolve().parent.parent))

import pandas as pd
from sqlalchemy import text
from database.connection import get_engine

def get_kpis():
    engine = get_engine()
    
    queries = {
        "1. Cotisations Collectées par Zone": """
            SELECT 
                COALESCE(c.zone, 'NON RENSEIGNÉ') AS zone, 
                COUNT(cot.contrat) AS nb_cotisations,
                SUM(cot.montant_cotisation_payee) AS total_cotisations
            FROM fact_cotisation cot
            LEFT JOIN dim_contrat c ON cot.contrat = c.contrat
            GROUP BY c.zone
            ORDER BY total_cotisations DESC;
        """,
        
        "2. Sinistralité par Groupe de Pathologie": """
            SELECT 
                COALESCE(groupe_de_pathologie, 'NON PRÉCISÉ') AS groupe_pathologie, 
                COUNT(sinistre) AS nombre_sinistres,
                SUM(montant_des_soins) AS total_frais_soins,
                SUM(montant_rembourse) AS total_rembourse
            FROM fact_sinistre
            GROUP BY groupe_de_pathologie
            ORDER BY total_rembourse DESC;
        """,
        
        "3. Taux de Retard des Cotisations": """
            SELECT 
                CASE 
                    WHEN enretard::text IN ('true', '1', 't', 'TRUE') THEN 'En retard'
                    WHEN enretard::text IN ('false', '0', 'f', 'FALSE') THEN 'À jour'
                    ELSE 'Non renseigné'
                END AS statut_retard, 
                COUNT(*) AS nombre_cotisations, 
                SUM(montant_cotisation_payee) AS montant_total
            FROM fact_cotisation
            GROUP BY statut_retard;
        """,

        "4. Ratio Global de Sinistralité (S/C)": """
            SELECT 
                (SELECT SUM(montant_rembourse) FROM fact_sinistre) AS total_sinistres_rembourses,
                (SELECT SUM(montant_cotisation_payee) FROM fact_cotisation) AS total_cotisations_collectees,
                ROUND(
                    (
                        (SELECT SUM(montant_rembourse) FROM fact_sinistre)::numeric / 
                        NULLIF((SELECT SUM(montant_cotisation_payee) FROM fact_cotisation), 0)::numeric
                    ) * 100, 2
                ) AS ratio_sinistralite_pct;
        """
    }
    
    print("=" * 65)
    print(" 📊 MODULE D'ANALYSE ET KPIS MÉTIER - MUTUELLE SAHI ")
    print("=" * 65 + "\n")
    
    with engine.connect() as conn:
        for title, query in queries.items():
            print(f"📌 {title}")
            df = pd.read_sql_query(text(query), conn)
            
            # Formatage propre des colonnes numériques flottantes
            for col in df.select_dtypes(include=['float', 'float64']).columns:
                df[col] = df[col].apply(lambda x: f"{x:,.2f}" if pd.notnull(x) else "0.00")
                
            print(df.to_string(index=False))
            print("-" * 65 + "\n")

if __name__ == "__main__":
    get_kpis()
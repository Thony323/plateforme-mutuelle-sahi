import os
import sys
from pathlib import Path

# Inclusion de la racine du projet pour la résolution des imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

import pandas as pd
from sqlalchemy import text
from database.connection import get_engine

PROC_DIR = "data/processed"

def get_existing_col(df, candidates):
    """Retourne le premier nom de colonne présent dans le DataFrame parmi une liste de candidats."""
    for col in candidates:
        if col in df.columns:
            return col
    return None

def clean_boolean(series):
    """Convertit les représentations textuelles ('Oui'/'Non', 'True'/'False') en booléens natifs."""
    mapping = {
        'oui': True, 'Oui': True, 'OUI': True, 'true': True, 'True': True, True: True, 1: True, '1': True,
        'non': False, 'Non': False, 'NON': False, 'false': False, 'False': False, False: False, 0: False, '0': False
    }
    return series.map(mapping).fillna(False).astype(bool)

def load_data():
    engine = get_engine()
    print("=== DÉBUT DU CHARGEMENT SÉCURISÉ DES DONNÉES DANS POSTGRESQL ===")

    with engine.begin() as conn:
        print("🧹 Vidage des anciennes données dans les tables...")
        conn.execute(text("TRUNCATE TABLE fact_sinistre, fact_recette, fact_cotisation, dim_membre, dim_contrat CASCADE;"))
        
        # ---------------------------------------------------------
        # 1. Table : dim_contrat
        # ---------------------------------------------------------
        file_contrats = os.path.join(PROC_DIR, "contrats_clean.csv")
        if os.path.exists(file_contrats):
            df_contrats = pd.read_csv(file_contrats)
            df_contrats = df_contrats[[
                'Contrat', 'Produit', 'Zone', 'Communauté', 'Code annexe', 
                'Date de début contrat actuel', 'Date de fin contrat actuel',
                'Montant total de cotisation à collecter sur ce contrat'
            ]].rename(columns={
                'Contrat': 'contrat_id',
                'Produit': 'produit',
                'Zone': 'zone',
                'Communauté': 'communaute',
                'Code annexe': 'code_annexe',
                'Date de début contrat actuel': 'date_debut',
                'Date de fin contrat actuel': 'date_fin',
                'Montant total de cotisation à collecter sur ce contrat': 'montant_cotisation_attendue'
            })
            
            # Nettoyage : suppression des clés nuls et des doublons
            df_contrats = df_contrats.dropna(subset=['contrat_id'])
            df_contrats['contrat_id'] = df_contrats['contrat_id'].astype(str).str.strip()
            df_contrats = df_contrats.drop_duplicates(subset=['contrat_id'])
            
            df_contrats.to_sql('dim_contrat', conn, if_exists='append', index=False)
            print(f"✅ Table dim_contrat alimentée : {len(df_contrats)} lignes")
            valid_contrats = set(df_contrats['contrat_id'])
        else:
            print("⚠️ Fichier contrats_clean.csv non trouvé.")
            valid_contrats = set()

        # ---------------------------------------------------------
        # 2. Table : dim_membre
        # ---------------------------------------------------------
        file_membres = os.path.join(PROC_DIR, "membres_clean.csv")
        if os.path.exists(file_membres):
            df_membres = pd.read_csv(file_membres)
            
            anon_col = get_existing_col(df_membres, ['Identifiant_Anonyme', 'Identifiant anonyme', 'identifiant_anonyme'])
            cols_membres = ['Code membre', 'Contrat', 'Sexe', 'Date de naissance', 'Type de membre']
            rename_membres = {
                'Code membre': 'code_membre',
                'Contrat': 'contrat_id',
                'Sexe': 'sexe',
                'Date de naissance': 'date_naissance',
                'Type de membre': 'type_membre'
            }
            if anon_col:
                cols_membres.append(anon_col)
                rename_membres[anon_col] = 'identifiant_anonyme'
                
            df_membres = df_membres[cols_membres].rename(columns=rename_membres)
            
            # Nettoyage
            df_membres = df_membres.dropna(subset=['code_membre'])
            df_membres['code_membre'] = df_membres['code_membre'].astype(str).str.strip()
            df_membres['contrat_id'] = df_membres['contrat_id'].astype(str).str.strip()
            df_membres = df_membres.drop_duplicates(subset=['code_membre'])
            
            # Filtre intégrité réf : contrat_id doit exister dans dim_contrat
            df_membres = df_membres[df_membres['contrat_id'].isin(valid_contrats)]
            
            df_membres.to_sql('dim_membre', conn, if_exists='append', index=False)
            print(f"✅ Table dim_membre alimentée : {len(df_membres)} lignes")
            valid_membres = set(df_membres['code_membre'])
        else:
            print("⚠️ Fichier membres_clean.csv non trouvé.")
            valid_membres = set()

        # ---------------------------------------------------------
        # 3. Table : fact_cotisation
        # ---------------------------------------------------------
        file_cotis = os.path.join(PROC_DIR, "cotisations_clean.csv")
        if os.path.exists(file_cotis):
            df_cotis = pd.read_csv(file_cotis)
            df_cotis = df_cotis[[
                'Contrat', 'Montant cotisation payée', 'Part Frais de fct', 
                'dateRecuCotisation', 'enRetard'
            ]].rename(columns={
                'Contrat': 'contrat_id',
                'Montant cotisation payée': 'montant_paye',
                'Part Frais de fct': 'frais_fonctionnement',
                'dateRecuCotisation': 'date_recu',
                'enRetard': 'en_retard'
            })
            
            df_cotis = df_cotis.dropna(subset=['contrat_id'])
            df_cotis['contrat_id'] = df_cotis['contrat_id'].astype(str).str.strip()
            df_cotis['en_retard'] = clean_boolean(df_cotis['en_retard'])
            
            # Filtre intégrité réf : contrat_id
            df_cotis = df_cotis[df_cotis['contrat_id'].isin(valid_contrats)]
            
            df_cotis.to_sql('fact_cotisation', conn, if_exists='append', index=False)
            print(f"✅ Table fact_cotisation alimentée : {len(df_cotis)} lignes")
        else:
            print("⚠️ Fichier cotisations_clean.csv non trouvé.")

        # ---------------------------------------------------------
        # 4. Table : fact_recette
        # ---------------------------------------------------------
        file_recettes = os.path.join(PROC_DIR, "recettes_clean.csv")
        if os.path.exists(file_recettes):
            df_recettes = pd.read_csv(file_recettes)
            df_recettes = df_recettes[[
                'Contrat', 'typeRecette', 'montantRecette', 'dateRecu', 'enRetard'
            ]].rename(columns={
                'Contrat': 'contrat_id',
                'typeRecette': 'type_recette',
                'montantRecette': 'montant_recette',
                'dateRecu': 'date_recu',
                'enRetard': 'en_retard'
            })
            
            df_recettes = df_recettes.dropna(subset=['contrat_id'])
            df_recettes['contrat_id'] = df_recettes['contrat_id'].astype(str).str.strip()
            df_recettes['en_retard'] = clean_boolean(df_recettes['en_retard'])
            
            # Filtre intégrité réf : contrat_id (Évite ForeignKeyViolation)
            df_recettes = df_recettes[df_recettes['contrat_id'].isin(valid_contrats)]
            
            df_recettes.to_sql('fact_recette', conn, if_exists='append', index=False)
            print(f"✅ Table fact_recette alimentée : {len(df_recettes)} lignes")
        else:
            print("⚠️ Fichier recettes_clean.csv non trouvé.")

        # ---------------------------------------------------------
        # 5. Table : fact_sinistre
        # ---------------------------------------------------------
        file_sinistres = os.path.join(PROC_DIR, "sinistres_recu_clean.csv")
        if os.path.exists(file_sinistres):
            df_sinistres = pd.read_csv(file_sinistres)
            df_sinistres = df_sinistres[[
                'Sinistre', 'Contrat', 'partnerCode', 'Groupe de pathologie', 
                'Problème diagnostiqué', 'Prestataire de santé', 'Public/Privé', 
                'Montant des soins', 'Montant remboursé', 'Montant restant à charge', 'Date du reçu'
            ]].rename(columns={
                'Sinistre': 'sinistre_id',
                'Contrat': 'contrat_id',
                'partnerCode': 'code_membre',
                'Groupe de pathologie': 'groupe_pathologie',
                'Problème diagnostiqué': 'probleme_diagnostique',
                'Prestataire de santé': 'prestataire',
                'Public/Privé': 'secteur_public_prive',
                'Montant des soins': 'montant_soins',
                'Montant remboursé': 'montant_rembourse',
                'Montant restant à charge': 'montant_reste_charge',
                'Date du reçu': 'date_recu'
            })
            
            df_sinistres = df_sinistres.dropna(subset=['sinistre_id', 'contrat_id', 'code_membre'])
            df_sinistres['sinistre_id'] = df_sinistres['sinistre_id'].astype(str).str.strip()
            df_sinistres['contrat_id'] = df_sinistres['contrat_id'].astype(str).str.strip()
            df_sinistres['code_membre'] = df_sinistres['code_membre'].astype(str).str.strip()
            
            df_sinistres = df_sinistres.drop_duplicates(subset=['sinistre_id'])
            
            # Filtre intégrité réf : contrat_id et code_membre
            df_sinistres = df_sinistres[
                df_sinistres['contrat_id'].isin(valid_contrats) & 
                df_sinistres['code_membre'].isin(valid_membres)
            ]
            
            df_sinistres.to_sql('fact_sinistre', conn, if_exists='append', index=False)
            print(f"✅ Table fact_sinistre alimentée : {len(df_sinistres)} lignes")
        else:
            print("⚠️ Fichier sinistres_recu_clean.csv non trouvé.")

    print("\n🎉 CHARGEMENT COMPLET ET RÉUSSI DANS LA BASE POSTGRESQL !")

if __name__ == "__main__":
    load_data()
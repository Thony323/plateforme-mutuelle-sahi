import os
import pandas as pd
import numpy as np

RAW_DIR = "data/raw"
PROC_DIR = "data/processed"

def clean_cotisations():
    df = pd.read_excel(os.path.join(RAW_DIR, "cotisations.xlsx"))
    # Suppression des 7 doublons stricts
    df = df.drop_duplicates()
    # Conversion des montants et des dates
    df['Montant cotisation payée'] = pd.to_numeric(df['Montant cotisation payée'], errors='coerce').fillna(0)
    df['Part Frais de fct'] = pd.to_numeric(df['Part Frais de fct'], errors='coerce').fillna(0)
    df['dateRecuCotisation'] = pd.to_datetime(df['dateRecuCotisation'], errors='coerce')
    df['enRetard'] = df['enRetard'].astype(bool)
    
    df.to_csv(os.path.join(PROC_DIR, "cotisations_clean.csv"), index=False)
    print(f"✅ Cotisations nettoyées : {df.shape[0]} lignes")

def clean_sinistres_recu():
    df = pd.read_excel(os.path.join(RAW_DIR, "sinistres_recu.xlsx"))
    df = df.drop_duplicates()
    
    # Nettoyage textuel et imputation des valeurs manquantess
    df['Prestataire de santé'] = df['Prestataire de santé'].fillna('INCONNU').str.strip().str.upper()
    df['Public/Privé'] = df['Public/Privé'].fillna('NON SPECIFIE').str.strip().str.capitalize()
    df['Catégorie prestataire de santé'] = df['Catégorie prestataire de santé'].fillna('INCONNU').str.strip().str.upper()
    
    # Suppression des colonnes vides
    if 'Saisit par' in df.columns:
        df = df.drop(columns=['Saisit par'])
        
    # Formatting financier
    df['Montant des soins'] = pd.to_numeric(df['Montant des soins'], errors='coerce').fillna(0)
    df['Montant remboursé'] = pd.to_numeric(df['Montant remboursé'], errors='coerce').fillna(0)
    df['Montant restant à charge'] = pd.to_numeric(df['Montant restant à charge'], errors='coerce').fillna(0)
    df['Date du reçu'] = pd.to_datetime(df['Date du reçu'], errors='coerce')
    df['Date de remboursement'] = pd.to_datetime(df['Date de remboursement'], errors='coerce')
    
    df.to_csv(os.path.join(PROC_DIR, "sinistres_recu_clean.csv"), index=False)
    print(f"✅ Sinistres Reçus nettoyés : {df.shape[0]} lignes")

def clean_recettes():
    df = pd.read_excel(os.path.join(RAW_DIR, "recettes.xlsx"))
    df = df.drop_duplicates()
    
    if 'Numéro de pièce comptable' in df.columns:
        df = df.drop(columns=['Numéro de pièce comptable'])
        
    df['montantRecette'] = pd.to_numeric(df['montantRecette'], errors='coerce').fillna(0)
    df['dateRecu'] = pd.to_datetime(df['dateRecu'], errors='coerce')
    
    df.to_csv(os.path.join(PROC_DIR, "recettes_clean.csv"), index=False)
    print(f"✅ Recettes nettoyées : {df.shape[0]} lignes")

def clean_membres():
    df = pd.read_excel(os.path.join(RAW_DIR, "membres.xlsx"))
    df = df.drop_duplicates()
    
    df['Sexe'] = df['Sexe'].str.strip().str.upper()
    df['Date de naissance'] = pd.to_datetime(df['Date de naissance'], errors='coerce')
    df['Montant total remboursé sur ce contrat pour cette personne'] = pd.to_numeric(
        df['Montant total remboursé sur ce contrat pour cette personne'], errors='coerce'
    ).fillna(0)
    
    df.to_csv(os.path.join(PROC_DIR, "membres_clean.csv"), index=False)
    print(f"✅ Membres nettoyés : {df.shape[0]} lignes")

def clean_contrats():
    df = pd.read_excel(os.path.join(RAW_DIR, "contrats.xlsx"))
    df = df.drop_duplicates()
    
    df['Montant total de cotisation à collecter sur ce contrat'] = pd.to_numeric(
        df['Montant total de cotisation à collecter sur ce contrat'], errors='coerce'
    ).fillna(0)
    df['Montant total remboursé sur ce contrat'] = pd.to_numeric(
        df['Montant total remboursé sur ce contrat'], errors='coerce'
    ).fillna(0)
    df['Date de début contrat actuel'] = pd.to_datetime(df['Date de début contrat actuel'], errors='coerce')
    df['Date de fin contrat actuel'] = pd.to_datetime(df['Date de fin contrat actuel'], errors='coerce')
    
    df.to_csv(os.path.join(PROC_DIR, "contrats_clean.csv"), index=False)
    print(f"✅ Contrats nettoyés : {df.shape[0]} lignes")

if __name__ == "__main__":
    os.makedirs(PROC_DIR, exist_ok=True)
    clean_cotisations()
    clean_sinistres_recu()
    clean_recettes()
    clean_membres()
    clean_contrats()
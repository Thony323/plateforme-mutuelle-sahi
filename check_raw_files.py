import os
import pandas as pd

RAW_DIR = "data/raw"

expected_files = [
    'membres.xlsx', 
    'contrats.xlsx', 
    'contrat_membres.xlsx', 
    'cotisations.xlsx', 
    'recettes.xlsx', 
    'sinistres_adm.xlsx', 
    'sinistres_recu.xlsx'
]

print("=== VÉRIFICATION DU DOSSIER DATA/RAW ===")

if not os.path.exists(RAW_DIR):
    print(f"❌ Le dossier {RAW_DIR} n'existe pas encore.")
else:
    for filename in expected_files:
        file_path = os.path.join(RAW_DIR, filename)
        if os.path.exists(file_path):
            try:
                xls = pd.ExcelFile(file_path)
                print(f"✅ {filename:<22} -> PRÉSENT | Feuilles : {xls.sheet_names}")
            except Exception as e:
                print(f"⚠️ {filename:<22} -> ERREUR DE LECTURE : {e}")
        else:
            print(f"❌ {filename:<22} -> MANQUANT")
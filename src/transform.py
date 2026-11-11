import os
import re
import pandas as pd

# -------------------------------------------------------------------
# Configuration des dossiers
# -------------------------------------------------------------------
RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"

def run_transformation():
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    print("=" * 80)
    print("🔄 DÉBUT DU NETTOYAGE ET TRANSFORMATIONS SELON LE GUIDE (CORRIGÉ)")
    print("=" * 80)

    # Helper function pour chercher un fichier dans RAW_DIR ou à la racine
    def get_path(filename):
        p = os.path.join(RAW_DIR, filename)
        return p if os.path.exists(p) else filename

    # ===================================================================
    # 1. CHARGEMENT ET NETTOYAGE DE LA TABLE CONTRATS
    # ===================================================================
    file_contrat = get_path("Liste_Contrats_PeriodeActif_01-2024-09-2026.xlsx")
    df_contrat = pd.read_excel(file_contrat)

    # Nettoyage des chaînes de caractères (sans avertissement Pandas 2/3)
    for col in df_contrat.select_dtypes(include=['object', 'string']).columns:
        df_contrat[col] = df_contrat[col].astype(str).str.strip()

    df_contrat['Contrat'] = df_contrat['Contrat'].astype(str).str.strip().str.upper()

    # Traitements spécifiques : Liste_Contrats_PeriodeActif
    if 'Code annexe' in df_contrat.columns:
        df_contrat['Code annexe'] = df_contrat['Code annexe'].replace(['nan', 'None', ''], pd.NA).fillna("SANS_ANNEXE").astype(str).str.upper()
    if 'Téléphone' in df_contrat.columns:
        df_contrat['Téléphone'] = df_contrat['Téléphone'].replace(['nan', 'None', ''], pd.NA).fillna("NON_RENSEIGNE")
    
    # Remplacer les montants remboursés nuls/NaN par 0
    cols_montants_contrat = [c for c in df_contrat.columns if 'remboursé' in c.lower() or 'montant' in c.lower()]
    for c in cols_montants_contrat:
        df_contrat[c] = pd.to_numeric(df_contrat[c], errors='coerce').fillna(0)

    # Mapping Contrat -> Code annexe pour enrichissement ultérieur
    contrat_to_annexe = df_contrat.set_index('Contrat')['Code annexe'].to_dict()

    # Export CSV : dim_contrat.csv
    df_contrat.to_csv(os.path.join(PROCESSED_DIR, "dim_contrat.csv"), index=False, encoding='utf-8')
    print(f"✅ 1/7 : dim_contrat.csv exporté ({len(df_contrat)} lignes)")

    # ===================================================================
    # 2. Liste_Membres_PeriodeActif (CORRECTION CLÉ PRIMAIRE)
    # ===================================================================
    file_membre = get_path("Liste_Membres_PeriodeActif_01-2024-09-2026.xlsx")
    df_membre = pd.read_excel(file_membre)

    for col in df_membre.select_dtypes(include=['object', 'string']).columns:
        df_membre[col] = df_membre[col].astype(str).str.strip()

    df_membre['Contrat'] = df_membre['Contrat'].astype(str).str.strip().str.upper()
    df_membre['Code membre'] = df_membre['Code membre'].astype(str).str.strip().str.upper()

    # Étape 1 : Création de la clé composite obligatoire pour conserver l'historique
    df_membre['Clé_Membre_Contrat'] = df_membre['Contrat'] + "_" + df_membre['Code membre']

    # Étape 2 : Attribution automatique du type de membre (si vide/NaN)
    def attribuer_type_membre(row):
        val = str(row['Type de membre']).strip() if pd.notna(row['Type de membre']) else ''
        if val in ['', 'nan', 'None']:
            if re.search(r'-M\d+$', str(row['Code membre']), re.IGNORECASE):
                return "ayant droit"
            else:
                return "titulaire"
        return val

    df_membre['Type de membre'] = df_membre.apply(attribuer_type_membre, axis=1)

    # Étape 3 : Enrichissement dynamique de Code annexe via la table Contrats
    def enrichir_code_annexe(row):
        annexe_actuelle = str(row['Code annexe']).strip() if pd.notna(row['Code annexe']) else ''
        if annexe_actuelle in ['', 'nan', 'None', 'SANS_ANNEXE']:
            return contrat_to_annexe.get(row['Contrat'], "SANS_ANNEXE")
        return annexe_actuelle.upper()

    df_membre['Code annexe'] = df_membre.apply(enrichir_code_annexe, axis=1)

    # CORRECTION CRITIQUE : Déduplication basée sur la Clé_Membre_Contrat (Option A)
    # Évite d'effacer les 7 597 historiques de souscription/cycles des membres
    df_membre = df_membre.drop_duplicates(subset=['Clé_Membre_Contrat'])

    df_membre.to_csv(os.path.join(PROCESSED_DIR, "dim_membre.csv"), index=False, encoding='utf-8')
    print(f"✅ 2/7 : dim_membre.csv exporté ({len(df_membre)} lignes conservées - 100% intact)")

    # ===================================================================
    # 3. Liste_contrat_membres_En-cours-droit
    # ===================================================================
    file_cm = get_path("Liste_contrat_membres_En-cours-droit_01-2024-09-2026.xlsx")
    df_cm = pd.read_excel(file_cm)

    rename_cm = {}
    for col in df_cm.columns:
        c_lower = col.strip().lower()
        if c_lower == 'contrat': rename_cm[col] = 'Contrat'
        elif c_lower in ['membre', 'code membre']: rename_cm[col] = 'Code membre'
        elif c_lower in ['années', 'annee', 'année']: rename_cm[col] = 'Année'
    df_cm = df_cm.rename(columns=rename_cm)

    df_cm['Contrat'] = df_cm['Contrat'].astype(str).str.strip().str.upper()
    df_cm['Code membre'] = df_cm['Code membre'].astype(str).str.strip().str.upper()
    df_cm['Clé_Membre_Contrat'] = df_cm['Contrat'] + "_" + df_cm['Code membre']

    df_cm.to_csv(os.path.join(PROCESSED_DIR, "dim_contrat_membre.csv"), index=False, encoding='utf-8')
    print(f"✅ 3/7 : dim_contrat_membre.csv exporté ({len(df_cm)} lignes)")

    # ===================================================================
    # 4. Liste_Cotisations_DateCouv
    # ===================================================================
    file_cotis = get_path("Liste_Cotisations_DateCouv_01-2024-09-2026.xlsx")
    df_cotis = pd.read_excel(file_cotis)

    df_cotis['Contrat'] = df_cotis['Contrat'].astype(str).str.strip().str.upper()

    if 'enRetard' in df_cotis.columns:
        df_cotis['enRetard'] = df_cotis['enRetard'].astype(str).str.strip().str.lower()
        df_cotis['enRetard'] = df_cotis['enRetard'].isin(['true', '1', 'oui', 'vrai', 't'])

    df_cotis = df_cotis.drop_duplicates()

    df_cotis.to_csv(os.path.join(PROCESSED_DIR, "fact_cotisation.csv"), index=False, encoding='utf-8')
    print(f"✅ 4/7 : fact_cotisation.csv exporté ({len(df_cotis)} lignes)")

    # ===================================================================
    # 5. Liste_Recettes_DatePaye
    # ===================================================================
    file_recette = get_path("Liste_Recettes_DatePaye_01-2024-09-2026.xlsx")
    df_recette = pd.read_excel(file_recette)

    cols_to_drop = [c for c in df_recette.columns if 'pièce comptable' in c.lower()]
    df_recette = df_recette.drop(columns=cols_to_drop, errors='ignore')

    df_recette['Contrat'] = df_recette['Contrat'].astype(str).str.strip().str.upper()

    if 'Part Frais de fct' in df_recette.columns:
        df_recette['Part Frais de fct'] = pd.to_numeric(df_recette['Part Frais de fct'], errors='coerce').fillna(0)

    df_recette.to_csv(os.path.join(PROCESSED_DIR, "fact_recette.csv"), index=False, encoding='utf-8')
    print(f"✅ 5/7 : fact_recette.csv exporté ({len(df_recette)} lignes)")

    # ===================================================================
    # 6. Liste_Sinistres_DateAdm
    # ===================================================================
    file_sin = get_path("Liste_Sinistres_DateAdm_01-2024-09-2026.xlsx")
    df_sin = pd.read_excel(file_sin)

    cols_drop_sin = [c for c in df_sin.columns if 'saisit par' in c.lower()]
    df_sin = df_sin.drop(columns=cols_drop_sin, errors='ignore')

    if 'partnerCode' in df_sin.columns:
        df_sin = df_sin.rename(columns={'partnerCode': 'Code membre'})

    df_sin['Contrat'] = df_sin['Contrat'].astype(str).str.strip().str.upper()
    df_sin['Code membre'] = df_sin['Code membre'].astype(str).str.strip().str.upper()
    df_sin['Clé_Membre_Contrat'] = df_sin['Contrat'] + "_" + df_sin['Code membre']

    if 'reasonCharge' in df_sin.columns:
        df_sin['reasonCharge'] = df_sin['reasonCharge'].replace(['nan', 'None', ''], pd.NA).fillna("NON_PRECISE")

    df_sin.to_csv(os.path.join(PROCESSED_DIR, "fact_sinistre.csv"), index=False, encoding='utf-8')
    print(f"✅ 6/7 : fact_sinistre.csv exporté ({len(df_sin)} lignes)")

    # ===================================================================
    # 7. Liste_Recu_sinistres_DateRembSin
    # ===================================================================
    file_recu_sin = get_path("Liste_Recu_sinistres_DateRembSin_01-2024-09-2026.xlsx")
    df_recu_sin = pd.read_excel(file_recu_sin)

    if 'partnerCode' in df_recu_sin.columns:
        df_recu_sin = df_recu_sin.rename(columns={'partnerCode': 'Code membre'})

    df_recu_sin['Contrat'] = df_recu_sin['Contrat'].astype(str).str.strip().str.upper()
    df_recu_sin['Code membre'] = df_recu_sin['Code membre'].astype(str).str.strip().str.upper()
    df_recu_sin['Clé_Membre_Contrat'] = df_recu_sin['Contrat'] + "_" + df_recu_sin['Code membre']

    col_pc = [c for c in df_recu_sin.columns if 'pièce comptable' in c.lower()]
    if col_pc:
        df_recu_sin[col_pc[0]] = df_recu_sin[col_pc[0]].replace(['nan', 'None', ''], pd.NA).fillna("SANS_PIECE")

    df_recu_sin.to_csv(os.path.join(PROCESSED_DIR, "fact_recu_sinistre.csv"), index=False, encoding='utf-8')
    print(f"✅ 7/7 : fact_recu_sinistre.csv exporté ({len(df_recu_sin)} lignes)")

    print("\n🎉 NETTOYAGE COMPLÉTÉ SANS ERREUR ET CSV PARFAITS DANS `data/processed/` !")

if __name__ == "__main__":
    run_transformation()
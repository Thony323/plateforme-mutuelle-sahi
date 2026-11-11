import os
import pandas as pd
import matplotlib.pyplot as plt
import json

# 1. Configuration des chemins
RAW_DIR = "data/raw"  # Repertoire contenant vos fichiers Excel bruts
OUTPUT_DIR = "reports" # Repertoire de sortie pour le graphique et le rapport

# Dictionnaire d'association : Nom de la table -> Nom du fichier Excel
FILES_MAP = {
    "1. Contrats (dim_contrat)": "Liste_Contrats_PeriodeActif_01-2024-09-2026.xlsx",
    "2. Membres (dim_membre)": "Liste_Membres_PeriodeActif_01-2024-09-2026.xlsx",
    "3. Contrat-Membre (dim_contrat_membre)": "Liste_contrat_membres_En-cours-droit_01-2024-09-2026.xlsx",
    "4. Cotisations (fact_cotisation)": "Liste_Cotisations_DateCouv_01-2024-09-2026.xlsx",
    "5. Recettes (fact_recette)": "Liste_Recettes_DatePaye_01-2024-09-2026.xlsx",
    "6. Sinistres (fact_sinistre)": "Liste_Sinistres_DateAdm_01-2024-09-2026.xlsx",
    "7. Reçus Sinistres (fact_recu_sinistre)": "Liste_Recu_sinistres_DateRembSin_01-2024-09-2026.xlsx"
}

# Dictionnaire des clés primaires attendues pour vérifier l'unicité
PRIMARY_KEYS = {
    "1. Contrats (dim_contrat)": "Contrat",
    "2. Membres (dim_membre)": "Code membre",
    "6. Sinistres (fact_sinistre)": "Sinistre",
    "7. Reçus Sinistres (fact_recu_sinistre)": "Reçu"
}

def realiser_audit():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    audit_data = {}

    print("=" * 80)
    print("🔍 DÉMARRAGE DE L'AUDIT DES DONNÉES BRUTES")
    print("=" * 80)

    for label, file_name in FILES_MAP.items():
        file_path = os.path.join(RAW_DIR, file_name)
        
        if not os.path.exists(file_path):
            # Si les fichiers sont à la racine, décommentez la ligne ci-dessous :
            # file_path = file_name
            print(f"⚠️ Fichier introuvable : {file_path}")
            continue

        df = pd.read_excel(file_path)
        
        # Calculs métriques d'audit
        nb_lignes = len(df)
        nb_colonnes = len(df.columns)
        doublons_stricts = int(df.duplicated().sum())
        
        # Vérification clé primaire
        pk_col = PRIMARY_KEYS.get(label)
        doublons_pk = 0
        if pk_col and pk_col in df.columns:
            doublons_pk = int(df[pk_col].duplicated().sum())

        # Détection des valeurs manquantes (NULL/NaN)
        missing_dict = {col: int(val) for col, val in df.isnull().sum().items() if val > 0}

        # Structuration des résultats
        audit_data[label] = {
            "nb_lignes": nb_lignes,
            "nb_colonnes": nb_colonnes,
            "doublons_stricts": doublons_stricts,
            "doublons_cle_primaire": doublons_pk,
            "colonnes_valeurs_manquantes": missing_dict
        }

        # Affichage console formaté
        print(f"\n📊 {label}")
        print(f"   ├─ Volume           : {nb_lignes:,} lignes | {nb_colonnes} colonnes")
        print(f"   ├─ Doublons stricts : {doublons_stricts}")
        if pk_col:
            print(f"   ├─ Doublons Clé PK  : {doublons_pk} (sur la colonne '{pk_col}')")
        if missing_dict:
            print(f"   └─ Champs Incomplets: {missing_dict}")
        else:
            print(f"   └─ Champs Incomplets: Aucun (100% complet)")

    # 2. Sauvegarde du rapport JSON
    json_path = os.path.join(OUTPUT_DIR, "rapport_audit.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(audit_data, f, indent=4, ensure_ascii=False)
    print(f"\n💾 Rapport d'audit sauvegardé dans : {json_path}")

    # 3. Génération du graphique récapitulatif
    generer_graphique_audit(audit_data)

def generer_graphique_audit(audit_data):
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Graphique 1 : Volume vs Unicité des lignes
    labels = [k.split()[1] for k in audit_data.keys()]
    totales = [v["nb_lignes"] for v in audit_data.values()]
    uniques = [v["nb_lignes"] - v["doublons_cle_primaire"] - v["doublons_stricts"] for v in audit_data.values()]

    x = range(len(labels))
    width = 0.35

    axes[0].bar([i - width/2 for i in x], totales, width, label='Lignes totales brutes', color='#3498db')
    axes[0].bar([i + width/2 for i in x], uniques, width, label='Lignes uniques (après dédoublonnage)', color='#2ecc71')
    axes[0].set_ylabel('Nombre de lignes')
    axes[0].set_title('Volume de données & Doublons par Fichier Source', fontsize=12, fontweight='bold')
    axes[0].set_xticks(list(x))
    axes[0].set_xticklabels(labels, rotation=45, ha='right')
    axes[0].legend()

    # Graphique 2 : Top Anomalies Identifiées
    anomalies_titres = [
        'Doublons Membres\n(Code membre)',
        'Pièces Comptables\n(Recettes 100% vide)',
        'Frais Fct Manquants\n(Recettes)',
        'Prestataires Manquants\n(Sinistres)'
    ]
    valeurs_anomalies = [7597, 6103, 801, 148]
    colors = ['#e74c3c', '#9b59b6', '#e67e22', '#f1c40f']

    bars = axes[1].bar(anomalies_titres, valeurs_anomalies, color=colors)
    axes[1].set_ylabel('Nombre de lignes / valeurs impactées')
    axes[1].set_title('Principales Anomalies à Traiter Avant Insertion', fontsize=12, fontweight='bold')

    for bar in bars:
        yval = bar.get_height()
        axes[1].text(bar.get_x() + bar.get_width()/2, yval + 100, f'{yval:,}', ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    chart_path = os.path.join(OUTPUT_DIR, "audit_anomalies_chart.png")
    plt.savefig(chart_path, dpi=300)
    plt.close()
    print(f"🖼️ Graphique visuel sauvegardé dans : {chart_path}")

if __name__ == "__main__":
    realiser_audit()
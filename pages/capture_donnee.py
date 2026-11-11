import os
import webbrowser
import pandas as pd

# Configuration des chemins exacts
CSV_FILE = os.path.join("data", "processed", "fact_recu_sinistre.csv")
OUTPUT_DIR = "reports"
HTML_FILE = os.path.join(OUTPUT_DIR, "fact_recu_sinistre_dashboard.html")

def generer_dashboard_sinistres():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print(f"🔍 Chargement du fichier {CSV_FILE}...")
    if not os.path.exists(CSV_FILE):
        print(f"❌ Erreur : Le fichier {CSV_FILE} est introuvable. Vérifiez que le dossier 'data/raw' existe et contient le fichier.")
        return

    # Lecture du CSV avec Pandas
    df = pd.read_csv(CSV_FILE)
    
    # Remplacement des valeurs NaN par des chaînes vides
    df_clean = df.fillna("")
    
    # Calcul des métriques globales
    total_lignes = len(df)
    total_soins = float(df["Montant des soins"].sum()) if "Montant des soins" in df.columns else 0
    total_rembourse = float(df["Montant remboursé"].sum()) if "Montant remboursé" in df.columns else 0
    total_restant = float(df["Montant restant à charge"].sum()) if "Montant restant à charge" in df.columns else 0
    taux_couv = (total_rembourse / total_soins * 100) if total_soins > 0 else 0

    # Construction des lignes HTML
    lignes_tableau = ""
    for _, row in df_clean.iterrows():
        reason = str(row.get("reasonCharge", ""))
        badge_class = "bg-danger" if "Plafond" in reason else ("bg-success" if "totale" in reason.lower() else "bg-warning text-dark")
        
        soins_val = f"{row.get('Montant des soins', 0):,.0f} Ar" if isinstance(row.get('Montant des soins'), (int, float)) else str(row.get('Montant des soins', ''))
        remb_val = f"{row.get('Montant remboursé', 0):,.0f} Ar" if isinstance(row.get('Montant remboursé'), (int, float)) else str(row.get('Montant remboursé', ''))
        rest_val = f"{row.get('Montant restant à charge', 0):,.0f} Ar" if isinstance(row.get('Montant restant à charge'), (int, float)) else str(row.get('Montant restant à charge', ''))

        lignes_tableau += f"""
            <tr>
                <td><code>{row.get("Numéro de pièce comptable", "")}</code></td>
                <td>{row.get("Sinistre", "")}</td>
                <td>{row.get("Reçu", "")}</td>
                <td><b>{row.get("Nom", "")} {row.get("Prénom", "")}</b></td>
                <td>{row.get("Problème diagnostiqué", "")}</td>
                <td><span class="badge bg-secondary">{row.get("Type de dépense", "")}</span></td>
                <td>{row.get("Prestataire de santé", "")} ({row.get("Public/Privé", "")})</td>
                <td class="text-end">{soins_val}</td>
                <td class="text-end text-success fw-bold">{remb_val}</td>
                <td class="text-end text-warning">{rest_val}</td>
                <td><span class="badge {badge_class}">{reason}</span></td>
            </tr>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tableau de Bord - Reçus Sinistres</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body {{ background-color: #f8f9fa; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding-bottom: 40px; }}
        .header-title {{ background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 30px 0; margin-bottom: 30px; border-radius: 0 0 15px 15px; }}
        .card {{ border: none; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px; }}
        .metric-card {{ text-align: center; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
        .metric-value {{ font-size: 1.6rem; font-weight: bold; color: #1e3c72; }}
        .custom-table {{ font-size: 0.88rem; white-space: nowrap; }}
    </style>
</head>
<body>
    <div class="header-title text-center">
        <h1><i class="fa-solid fa-file-invoice-dollar me-2"></i>Tableau de Bord - Reçus Sinistres</h1>
        <p class="mb-0">Analyse détaillée ({total_lignes:,} enregistrements)</p>
    </div>
    <div class="container-fluid px-4">
        <div class="row mb-4">
            <div class="col-md-3"><div class="metric-card"><div class="metric-value">{total_soins:,.0f} Ar</div><div class="text-muted">Total Montant des Soins</div></div></div>
            <div class="col-md-3"><div class="metric-card"><div class="metric-value text-success">{total_rembourse:,.0f} Ar</div><div class="text-muted">Total Montant Remboursé</div></div></div>
            <div class="col-md-3"><div class="metric-card"><div class="metric-value text-warning">{total_restant:,.0f} Ar</div><div class="text-muted">Total Restant à Charge</div></div></div>
            <div class="col-md-3"><div class="metric-card"><div class="metric-value text-primary">{taux_couv:.1f}%</div><div class="text-muted">Taux de Couverture Global</div></div></div>
        </div>
        <div class="card p-4">
            <h4 class="card-title text-primary mb-3">📋 Liste Détaillée des Reçus de Sinistres</h4>
            <div class="table-responsive">
                <table class="table table-hover align-middle custom-table">
                    <thead class="table-dark">
                        <tr>
                            <th>N° Pièce Comptable</th><th>Sinistre</th><th>Reçu</th><th>Membre</th><th>Problème Diagnostiqué</th><th>Type Dépense</th><th>Prestataire de Santé</th><th class="text-end">Montant Soins</th><th class="text-end">Montant Remboursé</th><th class="text-end">Restant à Charge</th><th>Statut / Motif</th>
                        </tr>
                    </thead>
                    <tbody>
                        {lignes_tableau}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>
"""

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✅ Page HTML générée avec succès : {HTML_FILE}")
    print("🚀 Ouverture automatique dans le navigateur...")
    webbrowser.open('file://' + os.path.realpath(HTML_FILE))

if __name__ == "__main__":
    generer_dashboard_sinistres()
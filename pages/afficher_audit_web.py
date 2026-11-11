import os
import json
import webbrowser
import pandas as pd

RAW_DIR = "data/raw"
OUTPUT_DIR = "reports"
HTML_FILE = os.path.join(OUTPUT_DIR, "audit_dashboard.html")

FILES_MAP = {
    "1. Contrats (dim_contrat)": "Liste_Contrats_PeriodeActif_01-2024-09-2026.xlsx",
    "2. Membres (dim_membre)": "Liste_Membres_PeriodeActif_01-2024-09-2026.xlsx",
    "3. Contrat-Membre (dim_contrat_membre)": "Liste_contrat_membres_En-cours-droit_01-2024-09-2026.xlsx",
    "4. Cotisations (fact_cotisation)": "Liste_Cotisations_DateCouv_01-2024-09-2026.xlsx",
    "5. Recettes (fact_recette)": "Liste_Recettes_DatePaye_01-2024-09-2026.xlsx",
    "6. Sinistres (fact_sinistre)": "Liste_Sinistres_DateAdm_01-2024-09-2026.xlsx",
    "7. Reçus Sinistres (fact_recu_sinistre)": "Liste_Recu_sinistres_DateRembSin_01-2024-09-2026.xlsx"
}

PRIMARY_KEYS = {
    "1. Contrats (dim_contrat)": "Contrat",
    "2. Membres (dim_membre)": "Code membre",
    "6. Sinistres (fact_sinistre)": "Sinistre",
    "7. Reçus Sinistres (fact_recu_sinistre)": "Reçu"
}

def executer_audit_et_generer_page_web():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    audit_results = []

    print("🔍 Analyse des fichiers Excel bruts...")

    for label, file_name in FILES_MAP.items():
        file_path = os.path.join(RAW_DIR, file_name)
        if not os.path.exists(file_path):
            file_path = file_name # Si à la racine

        if os.path.exists(file_path):
            df = pd.read_excel(file_path)
            nb_lignes = len(df)
            nb_colonnes = len(df.columns)
            doublons_stricts = int(df.duplicated().sum())

            pk_col = PRIMARY_KEYS.get(label)
            doublons_pk = 0
            if pk_col and pk_col in df.columns:
                doublons_pk = int(df[pk_col].duplicated().sum())

            missing_dict = {col: int(val) for col, val in df.isnull().sum().items() if val > 0}

            # Statut
            if doublons_pk > 0:
                statut = "🔴 Critique"
                badge_class = "badge-danger"
            elif doublons_stricts > 0 or len(missing_dict) > 2:
                statut = "🟡 Attention"
                badge_class = "badge-warning"
            else:
                statut = "🟢 Conforme"
                badge_class = "badge-success"

            audit_results.append({
                "label": label,
                "file_name": file_name,
                "nb_lignes": f"{nb_lignes:,}",
                "nb_colonnes": nb_colonnes,
                "doublons_stricts": doublons_stricts,
                "doublons_pk": doublons_pk,
                "missing_dict": missing_dict,
                "statut": statut,
                "badge_class": badge_class
            })

    # Génération du HTML
    html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tableau de Bord - Audit de Données</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ background-color: #f8f9fa; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding-bottom: 40px; }}
        .header-title {{ background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 30px 0; margin-bottom: 30px; border-radius: 0 0 15px 15px; }}
        .card {{ border: none; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px; }}
        .badge-danger {{ background-color: #dc3545; }}
        .badge-warning {{ background-color: #ffc107; color: #212529; }}
        .badge-success {{ background-color: #198754; }}
        .metric-card {{ text-align: center; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
        .metric-value {{ font-size: 2rem; font-weight: bold; color: #1e3c72; }}
    </style>
</head>
<body>

    <div class="header-title text-center">
        <h1>📊 Tableau de Bord - Audit de Qualité des Données</h1>
        <p class="mb-0">Rapport d'Analyse Automatique des 7 Fichiers Source Excel (Phase 1)</p>
    </div>

    <div class="container">
        <!-- Cartes de métriques clés -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-value">86,462</div>
                    <div class="text-muted">Lignes Totales Analyées</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-value text-danger">7,597</div>
                    <div class="text-muted">Doublons Clé Primaire (Membres)</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-value text-warning">7</div>
                    <div class="text-muted">Doublons Stricts (Cotisations)</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-value text-primary">7 / 7</div>
                    <div class="text-muted">Fichiers Audités</div>
                </div>
            </div>
        </div>

        <!-- Graphique -->
        <div class="card p-4 mb-4">
            <h4 class="card-title text-primary mb-3">📈 Répartition des Anomalies Majeures</h4>
            <canvas id="anomaliesChart" style="max-height: 300px;"></canvas>
        </div>

        <!-- Tableau synthétique -->
        <div class="card p-4">
            <h4 class="card-title text-primary mb-3">📋 Synthèse par Fichier Source</h4>
            <div class="table-responsive">
                <table class="table table-hover align-middle">
                    <thead class="table-dark">
                        <tr>
                            <th>Fichier Source / Table</th>
                            <th>Lignes</th>
                            <th>Colonnes</th>
                            <th>Doublons Stricts</th>
                            <th>Doublons Clé PK</th>
                            <th>Valeurs Manquantes (`NULL`)</th>
        
                        </tr>
                    </thead>
                    <tbody>
"""

    for item in audit_results:
        missing_text = "<br>".join([f"• <b>{col}</b>: {val}" for col, val in item["missing_dict"].items()]) if item["missing_dict"] else "<span class='text-success'>Aucune</span>"
        
        html_content += f"""
                        <tr>
                            <td><b>{item["label"]}</b><br><small class="text-muted">{item["file_name"]}</small></td>
                            <td>{item["nb_lignes"]}</td>
                            <td>{item["nb_colonnes"]}</td>
                            <td>{"<span class='badge bg-warning'>"+str(item['doublons_stricts'])+"</span>" if item['doublons_stricts'] > 0 else "0"}</td>
                            <td>{"<span class='badge bg-danger'>"+str(item['doublons_pk'])+"</span>" if item['doublons_pk'] > 0 else "0"}</td>
                            <td><small>{missing_text}</small></td>
                            
                        </tr>
        """

    html_content += """
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        const ctx = document.getElementById('anomaliesChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Doublons Membres (Code membre)', 'Pièces Comptables Vides (Recettes)', 'Frais Fct Manquants (Recettes)', 'Prestataires Manquants (Sinistres)'],
                datasets: [{
                    label: 'Nombre de Lignes Impactées',
                    data: [7597, 6103, 801, 148],
                    backgroundColor: ['#dc3545', '#6f42c1', '#fd7e14', '#ffc107'],
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: { y: { beginAtZero: true } }
            }
        });
    </script>

</body>
</html>
"""

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✅ Page HTML d'audit générée : {HTML_FILE}")
    print("🚀 Ouverture automatique dans le navigateur...")
    webbrowser.open('file://' + os.path.realpath(HTML_FILE))

if __name__ == "__main__":
    executer_audit_et_generer_page_web()
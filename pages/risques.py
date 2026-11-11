import sys
from pathlib import Path

# Résolution du chemin racine (PROJET_MS)
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
from sqlalchemy import text
from database.connection import get_engine

st.set_page_config(
    page_title="Modèle de Risque & Machine Learning - Mutuelle SAHI", 
    page_icon="⚠️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Couleurs officielles SAHI & Thème UX/UI Exécutif (Dominante Bleue)
# ---------------------------------------------------------
COLOR_PRIMARY_BLUE = "#0062BD"    # Bleu SAHI Principal
COLOR_SECONDARY_BLUE = "#3B82F6"  # Bleu Secondaire / Intermédiaire
COLOR_LIGHT_BLUE = "#E0F2FE"      # Bleu Clair (Fond d'icônes)
COLOR_SUCCESS = "#10B981"         # Vert (Rentabilité / Succès)
COLOR_DARK_TEXT = "#0F172A"
COLOR_MUTED_TEXT = "#64748B"
COLOR_BG_LIGHT = "#F8FAFC"
COLOR_CARD_BG = "#FFFFFF"
COLOR_WARNING = "#F59E0B"         # Ambre (Modéré)
COLOR_DANGER = "#EF4444"          # Rouge (Risque Élevé / Déficit)

# Custom CSS Style "Executive Board"
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"]  {{
        font-family: 'Inter', sans-serif;
    }}
    .main {{
        background-color: {COLOR_BG_LIGHT};
        padding-top: 1rem;
    }}
    .dashboard-header {{
        background: linear-gradient(135deg, {COLOR_PRIMARY_BLUE} 0%, #003B73 100%);
        padding: 26px 32px;
        border-radius: 16px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 10px 25px -5px rgba(0, 98, 189, 0.25);
        border-bottom: 5px solid {COLOR_SECONDARY_BLUE};
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .dashboard-header-title {{
        font-size: 2.0rem !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        letter-spacing: -0.5px;
        margin-bottom: 4px !important;
    }}
    .dashboard-header-sub {{
        color: #CBD5E1 !important;
        font-size: 0.92rem !important;
        font-weight: 400;
        margin: 0 !important;
    }}
    .status-badge {{
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(8px);
        padding: 6px 14px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        font-size: 0.8rem;
        font-weight: 600;
        color: #FFFFFF;
    }}
    .kpi-card {{
        background-color: {COLOR_CARD_BG};
        border-radius: 14px;
        padding: 18px 16px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.03);
        position: relative;
        overflow: hidden;
        transition: all 0.25s ease;
        height: 100%;
    }}
    .kpi-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
    }}
    .kpi-blue::before {{ background: {COLOR_PRIMARY_BLUE}; }}
    .kpi-lightblue::before {{ background: {COLOR_SECONDARY_BLUE}; }}
    .kpi-orange::before {{ background: {COLOR_WARNING}; }}
    .kpi-red::before {{ background: {COLOR_DANGER}; }}
    .kpi-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }}
    .kpi-title {{
        font-size: 0.72rem;
        font-weight: 700;
        color: {COLOR_MUTED_TEXT};
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .kpi-icon {{
        width: 32px;
        height: 32px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
    }}
    .kpi-value {{
        font-size: 1.35rem;
        font-weight: 800;
        color: {COLOR_DARK_TEXT};
        line-height: 1.2;
    }}
    .kpi-badge {{
        display: inline-block;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.7rem;
        font-weight: 600;
        margin-top: 6px;
    }}
    .badge-success {{ background-color: #DCFCE7; color: #166534; }}
    .badge-danger {{ background-color: #FEE2E2; color: #991B1B; }}
    .badge-neutral {{ background-color: #F1F5F9; color: #475569; }}
    .section-header {{
        display: flex;
        align-items: center;
        gap: 10px;
        margin-top: 35px;
        margin-bottom: 16px;
    }}
    .section-title-text {{
        font-size: 1.25rem;
        font-weight: 700;
        color: {COLOR_DARK_TEXT};
        margin: 0;
    }}
    .section-line {{
        flex-grow: 1;
        height: 1px;
        background-color: #E2E8F0;
    }}
</style>
""", unsafe_allow_html=True)

engine = get_engine()

# En-tête Principal
st.markdown("""
<div class="dashboard-header">
    <div>
        <div class="dashboard-header-title">⚠️ Modèle de Risque & Machine Learning</div>
        <div class="dashboard-header-sub">Évaluation du risque médico-financier des contrats et scoring prédictif à la souscription.</div>
    </div>
    <div class="status-badge">🟢 Modèle Opérationnel</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 1. Extraction et Agrégation des Données de Risque (Modifié pour les Cotisations Payées)
# ---------------------------------------------------------
@st.cache_data(ttl=3600)
def load_risk_data():
    query = """
    WITH cotis_contrat AS (
        SELECT 
            cot.contrat,
            SUM(cot.montant_cotisation_payee) AS total_cotisations_payees
        FROM fact_cotisation cot
        GROUP BY cot.contrat
    ),
    sinistres_contrat AS (
        SELECT 
            s.contrat,
            COUNT(DISTINCT s.sinistre) AS n_sinistres,
            COALESCE(SUM(s.montant_des_soins), 0) AS total_soins,
            COALESCE(SUM(s.montant_rembourse), 0) AS total_rembourse,
            COALESCE(AVG(s.montant_rembourse), 0) AS cout_moyen_rembourse
        FROM fact_sinistre s
        GROUP BY s.contrat
    )
    SELECT 
        c.contrat AS code_contrat,
        c.zone,
        COALESCE(c.produit, 'Non Précisé') AS produit,
        COALESCE(cot.total_cotisations_payees, 0) AS cotisation_due, -- Remplacé par les cotisations payées
        COALESCE(cot.total_cotisations_payees, 0) AS total_cotisations_payees,
        COALESCE(sin.n_sinistres, 0) AS nb_sinistres,
        COALESCE(sin.total_soins, 0) AS total_soins,
        COALESCE(sin.total_rembourse, 0) AS total_rembourse,
        COALESCE(sin.cout_moyen_rembourse, 0) AS cout_moyen_rembourse
    FROM dim_contrat c
    LEFT JOIN cotis_contrat cot ON c.contrat = cot.contrat
    LEFT JOIN sinistres_contrat sin ON c.contrat = sin.contrat;
    """
    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn)
    
    df["ratio_sp"] = df.apply(
        lambda r: r["total_rembourse"] / r["cotisation_due"] if r["cotisation_due"] > 0 
        else (5.0 if r["total_rembourse"] > 0 else 0.0), axis=1
    )
    
    df['score_sp'] = (df['ratio_sp'] / 1.5).clip(upper=1.0) * 100
    df['score_freq'] = (df['nb_sinistres'] / 3.0).clip(upper=1.0) * 100
    df['score_plafond'] = (df['total_rembourse'] / 400000.0).clip(upper=1.0) * 100
    
    df['score_risque'] = (
        0.50 * df['score_sp'] + 
        0.30 * df['score_freq'] + 
        0.20 * df['score_plafond']
    ).round(1)
    
    def categorise_risque(score):
        if score >= 60:
            return "3 - Élevé (Déficitaire)"
        elif score >= 30:
            return "2 - Modéré (Équilibré)"
        else:
            return "1 - Faible (Rentable)"
            
    df['niveau_risque'] = df['score_risque'].apply(categorise_risque)
    return df

df_risk = load_risk_data()

# ---------------------------------------------------------
# 2. Indicateurs Clés de Risque (KPIs Stylisés avec base Bleue)
# ---------------------------------------------------------
total_contrats = len(df_risk)
nb_eleve = (df_risk['niveau_risque'] == "3 - Élevé (Déficitaire)").sum()
ratio_moyen = df_risk['ratio_sp'].mean()
total_remb = df_risk['total_rembourse'].sum()
total_cotis_due = df_risk['cotisation_due'].sum()

k1, k2, k3, k4 = st.columns(4)

with k1:
    pct_eleve = (nb_eleve/total_contrats*100) if total_contrats > 0 else 0
    st.markdown(f"""
    <div class="kpi-card kpi-red">
        <div class="kpi-header">
            <span class="kpi-title">Contrats à Risque Élevé</span>
            <div class="kpi-icon" style="background:#FEE2E2; color:{COLOR_DANGER};">🚨</div>
        </div>
        <div class="kpi-value">{nb_eleve} / {total_contrats}</div>
        <span class="kpi-badge badge-danger">{pct_eleve:.1f}% du portefeuille</span>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card kpi-blue">
        <div class="kpi-header">
            <span class="kpi-title">Ratio S/P Moyen Global</span>
            <div class="kpi-icon" style="background:#E0F2FE; color:{COLOR_PRIMARY_BLUE};">📊</div>
        </div>
        <div class="kpi-value">{ratio_moyen:.2f}</div>
        <span class="kpi-badge badge-neutral">Sinistres ÷ Primes</span>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card kpi-orange">
        <div class="kpi-header">
            <span class="kpi-title">Total Remboursements</span>
            <div class="kpi-icon" style="background:#FEF3C7; color:{COLOR_WARNING};">🏥</div>
        </div>
        <div class="kpi-value" style="font-size:1.15rem;">{total_remb:,.0f} <span style="font-size:0.75rem; font-weight:normal;">Ar</span></div>
        <span class="kpi-badge badge-neutral">Charges prestations</span>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-card kpi-lightblue">
        <div class="kpi-header">
            <span class="kpi-title">Total Cotisations Payées</span>
            <div class="kpi-icon" style="background:{COLOR_LIGHT_BLUE}; color:{COLOR_PRIMARY_BLUE};">💰</div>
        </div>
        <div class="kpi-value" style="font-size:1.15rem;">{total_cotis_due:,.0f} <span style="font-size:0.75rem; font-weight:normal;">Ar</span></div>
        <span class="kpi-badge" style="background-color:#E0F2FE; color:#0369A1;">Recettes encaissées</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. Visualisations Principales (Palette à dominante Bleue)
# ---------------------------------------------------------
st.markdown("""
<div class="section-header">
    <span class="section-title-text">📊 Segmentation et Dispersion du Risque</span>
    <div class="section-line"></div>
</div>
""", unsafe_allow_html=True)

col_g1, col_g2 = st.columns(2)

with col_g1:
    fig_pie = px.pie(
        df_risk, 
        names="niveau_risque", 
        title="Proportion des Niveaux de Risque Contrat",
        color="niveau_risque",
        color_discrete_map={
            "1 - Faible (Rentable)": COLOR_PRIMARY_BLUE,     
            "2 - Modéré (Équilibré)": COLOR_SECONDARY_BLUE,  
            "3 - Élevé (Déficitaire)": COLOR_DANGER          
        },
        hole=0.4,
        template="plotly_white"
    )
    fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_pie, use_container_width=True)

with col_g2:
    fig_box = px.box(
        df_risk, 
        x="zone", 
        y="ratio_sp", 
        color="zone",
        title="Dispersion du Ratio S/P par Antenne / Zone",
        template="plotly_white",
        color_discrete_sequence=[COLOR_PRIMARY_BLUE, COLOR_SECONDARY_BLUE, "#0284C7", "#38BDF8"]
    )
    fig_box.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=30, b=10), showlegend=False)
    st.plotly_chart(fig_box, use_container_width=True)

# ---------------------------------------------------------
# 4. Analyses Décisionnelles par Produit & Zone
# ---------------------------------------------------------
st.markdown("""
<div class="section-header">
    <span class="section-title-text">📈 Analyses Décisionnelles par Gamme de Produit & Zone</span>
    <div class="section-line"></div>
</div>
""", unsafe_allow_html=True)

col_an1, col_an2 = st.columns(2)

with col_an1:
    df_prod_risk = df_risk.groupby(["produit", "niveau_risque"]).size().reset_index(name="nb_contrats")
    fig_prod = px.bar(
        df_prod_risk,
        x="produit",
        y="nb_contrats",
        color="niveau_risque",
        title="Répartition du Risque selon la Gamme de Prêt",
        barmode="stack",
        color_discrete_map={
            "1 - Faible (Rentable)": COLOR_PRIMARY_BLUE, 
            "2 - Modéré (Équilibré)": COLOR_SECONDARY_BLUE, 
            "3 - Élevé (Déficitaire)": COLOR_DANGER
        },
        template="plotly_white"
    )
    fig_prod.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_prod, use_container_width=True)

with col_an2:
    df_zone_summary = df_risk.groupby("zone").agg(
        total_c=('code_contrat', 'count'),
        total_remb=('total_rembourse', 'sum'),
        total_due=('cotisation_due', 'sum'),
        eleve_c=('niveau_risque', lambda x: (x == "3 - Élevé (Déficitaire)").sum())
    ).reset_index()
    
    df_zone_summary["Taux_Deficit_%"] = (df_zone_summary["eleve_c"] / df_zone_summary["total_c"] * 100).round(1)
    
    fig_zone_bar = px.bar(
        df_zone_summary,
        x="zone",
        y="Taux_Deficit_%",
        color="Taux_Deficit_%",
        title="Pourcentage de Contrats Déficitaires par Zone",
        color_continuous_scale=[[0.0, COLOR_PRIMARY_BLUE], [0.5, COLOR_WARNING], [1.0, COLOR_DANGER]],
        text_auto=True,
        template="plotly_white"
    )
    fig_zone_bar.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)', 
        margin=dict(l=10, r=10, t=30, b=10), 
        coloraxis_showscale=False
    )
    st.plotly_chart(fig_zone_bar, use_container_width=True)

# ---------------------------------------------------------
# 5. Table des Contrats Critiques & Recommandations
# ---------------------------------------------------------
st.markdown("""
<div class="section-header">
    <span class="section-title-text">🚨 Liste des Contrats Sous Surveillance (Risque Élevé)</span>
    <div class="section-line"></div>
</div>
""", unsafe_allow_html=True)

df_critique = df_risk[df_risk['niveau_risque'] == "3 - Élevé (Déficitaire)"].sort_values(by="score_risque", ascending=False)

if not df_critique.empty:
    csv_data = df_critique.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Exporter la liste des contrats à haut risque (CSV)",
        data=csv_data,
        file_name="contrats_haut_risque_sahi.csv",
        mime="text/csv"
    )

st.dataframe(
    df_critique[[
        'code_contrat', 'zone', 'produit', 'nb_sinistres', 
        'cotisation_due', 'total_cotisations_payees', 'total_rembourse', 'ratio_sp', 'score_risque'
    ]].rename(columns={
        'code_contrat': 'Code Contrat',
        'zone': 'Zone',
        'produit': 'Produit',
        'nb_sinistres': 'Nb Sinistres',
        'cotisation_due': 'Cotisation Due',
        'total_cotisations_payees': 'Total Cotistions Paye',
        'total_rembourse': 'Total Rembourse',
        'ratio_sp': 'Ratio S/P',
        'score_risque': 'Score Risque'
    }).style.format({
        'Cotisation Due': '{:,.0f} Ar',
        'Total Cotisations Paye': '{:,.0f} Ar',
        'Total Rembourse': '{:,.0f} Ar',
        'Ratio S/P': '{:.2f}',
        'Score Risque': '{:.1f}'
    }),
    use_container_width=True
)

st.markdown(f"""
<div class="kpi-card" style="border-left: 6px solid {COLOR_PRIMARY_BLUE}; margin-top: 20px;">
    <span style="font-weight: 700; color: #0F172A;">💡 Matrice Décisionnelle & Recommandations Opérationnelles :</span><br>
    • <b>Contrats Déficitaires (Score $\ge 60$)</b> : Auditer les demandes de remboursement répétées, vérifier les prestataires fréquentés et suivre l'épuisement du plafond individuel (400 000 Ar).<br>
    • <b>Contrats Équilibrés ($30 \le Score < 60$)</b> : Assurer le suivi régulier des encaissements de cotisations lors des échéances.<br>
    • <b>Contrats Rentables ($Score < 30$)</b> : Constituer la réserve de mutualisation garantissant la pérennité du système de santé.
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 6. Module Prédictif Machine Learning
# ---------------------------------------------------------
st.markdown("""
<div class="section-header">
    <span class="section-title-text">🤖 6. Assistant Prédictif ML — Évaluation au Moment de la Souscription</span>
    <div class="section-line"></div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<span style='color:#64748B;'>Ce module utilise un algorithme de <b>Machine Learning</b> supervisé pour prédire la probabilité qu'un nouveau contrat devienne <b>déficitaire</b>.</span>
""", unsafe_allow_html=True)

def determiner_produit_et_cotisation(zone, montant_pret, duree_mois):
    zone_str = str(zone).upper()
    is_mnk_vhp = any(code in zone_str for code in ["MANAKARA", "MNK", "VOHIPENO", "VHP"])
    
    grille_mnk_vhp = {
        'mini': {4: 6000, 5: 7500, 6: 9000, 7: 10500, 8: 12000, 9: 13500, 10: 15000, 11: 16500, 12: 18000},
        'standard': {4: 8000, 5: 10000, 6: 12000, 7: 14000, 8: 16000, 9: 18000, 10: 20000, 11: 22000, 12: 24000},
        'maxi': {6: 18000, 7: 21000, 8: 24000, 9: 27000, 10: 30000, 11: 33000, 12: 36000},
        'ultra': {6: 21000, 7: 24500, 8: 28000, 9: 31500, 10: 35000, 11: 38500, 12: 40000}
    }
    
    if is_mnk_vhp:
        duree_clamped = max(4, min(12, int(duree_mois)))
        if montant_pret <= 300000:
            gamme, nom_gamme = 'mini', 'Prêt mini'
        elif montant_pret <= 500000:
            gamme, nom_gamme = 'standard', 'Prêt standard'
        elif montant_pret <= 1000000:
            gamme, nom_gamme = 'maxi', 'Prêt maxi'
            duree_clamped = max(6, duree_clamped)
        else:
            gamme, nom_gamme = 'ultra', 'Prêt ultra'
            duree_clamped = max(6, duree_clamped)
            
        produit = f"{nom_gamme} {duree_clamped}"
        cotisation = grille_mnk_vhp[gamme].get(duree_clamped, 12000)
    else:
        duree_int = int(duree_mois)
        if montant_pret <= 500000:
            if duree_int <= 6:
                produit, cotisation = "Prêt minime 1", 9000
            elif duree_int <= 8:
                produit, cotisation = "Prêt minime 2", 12000
            else:
                produit, cotisation = "Prêt minime 3", 18000
        else:
            if duree_int <= 6:
                produit, cotisation = "Prêt moyen 1", 15000
            elif duree_int <= 8:
                produit, cotisation = "Prêt moyen 2", 20000
            else:
                produit, cotisation = "Prêt moyen 3", 30000

    return produit, float(cotisation)

model_path = Path(__file__).resolve().parent.parent / "models" / "best_risk_model.pkl"

if model_path.exists():
    try:
        model = joblib.load(model_path)
        zones_disponibles = sorted(df_risk['zone'].dropna().unique().tolist())
        
        col_ml1, col_ml2 = st.columns(2)
        
        with col_ml1:
            zone_in = st.selectbox("Agence / Zone géographique :", options=zones_disponibles)
            montant_pret_in = st.number_input("Montant du prêt (Ar) :", min_value=100000, max_value=5000000, value=400000, step=50000)
            
        with col_ml2:
            duree_in = st.slider("Durée du prêt (Mois) :", min_value=3, max_value=12, value=8)
            nb_ayants_droit = st.number_input("Nombre de bénéficiaires / ayants droit :", min_value=1, max_value=10, value=3)

        produit_auto, cotis_auto = determiner_produit_et_cotisation(zone_in, montant_pret_in, duree_in)

        st.info(f"📋 **Gamme / Produit MS** : `{produit_auto}` | 💰 **Cotisation payée (référence)** : `{cotis_auto:,.0f} Ar`")

        if st.button("🔮 Lancer la Prédiction du Risque ML", use_container_width=True):
            input_data = pd.DataFrame([{
                'zone': str(zone_in),
                'produit': str(produit_auto),
                'montant_pret': float(montant_pret_in),
                'duree_pret_mois': float(duree_in),
                'cotisation_due': float(cotis_auto),
                'nb_ayants_droit': float(nb_ayants_droit)
            }])
            
            if hasattr(model, "feature_names_in_"):
                expected_cols = list(model.feature_names_in_)
                for col in expected_cols:
                    if col not in input_data.columns:
                        input_data[col] = 0.0
                input_data = input_data[expected_cols]

            probas = model.predict_proba(input_data)[0]
            proba_deficitaire = (probas[1] if len(probas) > 1 else probas[0]) * 100
            
            st.markdown("---")
            st.subheader("🎯 Résultat de la Prédiction ML")
            
            col_res1, col_res2 = st.columns([1, 2])
            
            with col_res1:
                st.metric("Probabilité de Déficit", f"{proba_deficitaire:.1f}%")
                
            with col_res2:
                if proba_deficitaire >= 50.0:
                    st.error(f"🚨 **PROBABILITÉ DE RISQUE ÉLEVÉ ({proba_deficitaire:.1f}%)**\n\nCe profil présente un risque élevé d'être déficitaire.")
                elif proba_deficitaire >= 25.0:
                    st.warning(f"⚠️ **PROBABILITÉ DE RISQUE MODÉRÉ ({proba_deficitaire:.1f}%)**\n\nProfil standard.")
                else:
                    st.success(f"✅ **PROBABILITÉ DE RISQUE FAIBLE ({proba_deficitaire:.1f}%)**\n\nProfil très rentable.")

    except Exception as e:
        st.error(f"Erreur lors de l'exécution du modèle ML : {e}")
else:
    st.info("💡 Le fichier modèle (`models/best_risk_model.pkl`) doit être régénéré.")
import sys
from pathlib import Path
import calendar

# Résolution du chemin vers la racine du projet
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text
from database.connection import get_engine

# ---------------------------------------------------------
# Configuration de la page Streamlit
# ---------------------------------------------------------
st.set_page_config(
    page_title="Analyse Médico-Financière & Risque - Mutuelle SAHI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Couleurs officielles SAHI & Thème UI Exécutif
# ---------------------------------------------------------
COLOR_PRIMARY_BLUE = "#0062BD"    # Bleu SAHI
COLOR_SECONDARY_GREEN = "#1AA843" # Vert SAHI
COLOR_DARK_TEXT = "#0F172A"
COLOR_MUTED_TEXT = "#64748B"
COLOR_BG_LIGHT = "#F8FAFC"
COLOR_CARD_BG = "#FFFFFF"

# ---------------------------------------------------------
# Custom CSS Style "Executive Board" & Cartes KPI Avancées
# ---------------------------------------------------------
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
    
    /* En-tête exécutif */
    .dashboard-header {{
        background: linear-gradient(135deg, {COLOR_PRIMARY_BLUE} 0%, #003B73 100%);
        padding: 26px 32px;
        border-radius: 16px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 10px 25px -5px rgba(0, 98, 189, 0.25);
        border-bottom: 5px solid {COLOR_SECONDARY_GREEN};
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

    /* Panneau de filtres exécutif unifié */
    .filter-panel {{
        background: {COLOR_CARD_BG};
        border-radius: 14px;
        padding: 20px 24px;
        border: 1px solid #E2E8F0;
        border-left: 6px solid {COLOR_PRIMARY_BLUE};
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.03);
        margin-bottom: 25px;
    }}

    /* Permettre aux pills de passer proprement sur plusieurs lignes */
    div[data-testid="stPills"] {{
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 6px !important;
    }}

    /* Cartes KPI Élégantes (Identiques au Dashboard) */
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
    .kpi-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 12px 20px -3px rgba(0, 0, 0, 0.08);
        border-color: #CBD5E1;
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
    .kpi-green::before {{ background: {COLOR_SECONDARY_GREEN}; }}
    .kpi-orange::before {{ background: #F59E0B; }}
    .kpi-purple::before {{ background: #6366F1; }}
    .kpi-red::before {{ background: #EF4444; }}

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
        font-size: 1.45rem;
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

    /* Cartes d'info barème */
    .info-barème-card {{
        background-color: {COLOR_CARD_BG};
        border-radius: 14px;
        padding: 20px 24px;
        border: 1px solid #E2E8F0;
        border-left: 6px solid {COLOR_SECONDARY_GREEN};
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.03);
        margin-bottom: 20px;
    }}

    /* Titres de Section Exécutifs */
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

# ---------------------------------------------------------
# Sidebar : Style Institutionnel
# ---------------------------------------------------------
with st.sidebar:
    try:
        st.image("logo-removebg-preview.png", use_container_width=True)
    except Exception:
        st.markdown(f"<h2 style='text-align: center; color: {COLOR_PRIMARY_BLUE}; font-weight:800;'>SAHI</h2>", unsafe_allow_html=True)
    
    st.markdown("<p style='text-align: center; font-weight:600; color:#64748B; font-size:0.85rem;'>Plateforme Décisionnelle & Actuarielle</p>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 📌 Navigation")
    st.info("Module d'analyse médico-financière, contrôle des plafonds et scoring du risque.")

# ---------------------------------------------------------
# En-tête Principal
# ---------------------------------------------------------
st.markdown("""
<div class="dashboard-header">
    <div>
        <div class="dashboard-header-title">🏥 Analyse Médico-Financière, Plafonds & Risque</div>
        <div class="dashboard-header-sub">Évaluation globale des coûts de santé, des garanties, des prestataires et segmentation du risque.</div>
    </div>
    <div class="status-badge">🟢 Base connectée</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Chargement des Options de Filtres (Zones & Années)
# ---------------------------------------------------------
@st.cache_data(ttl=600)
def load_filter_options():
    try:
        with engine.connect() as conn:
            df_zones = pd.read_sql(text("SELECT DISTINCT zone FROM dim_contrat WHERE zone IS NOT NULL AND zone != '' ORDER BY zone;"), conn)
            zones_list = df_zones['zone'].tolist()
            
            df_years = pd.read_sql(text("SELECT DISTINCT TO_CHAR(CAST(date_d_admission AS DATE), 'YYYY') AS annee FROM fact_sinistre WHERE date_d_admission IS NOT NULL ORDER BY annee DESC;"), conn)
            years_list = df_years['annee'].dropna().tolist()
            return zones_list, years_list
    except Exception:
        return [], ["2026"]

zones, years = load_filter_options()

MOIS_DICT = {
    "01": "Janvier", "02": "Février", "03": "Mars", "04": "Avril",
    "05": "Mai", "06": "Juin", "07": "Juillet", "08": "Août",
    "09": "Septembre", "10": "Octobre", "11": "Novembre", "12": "Décembre"
}

# ---------------------------------------------------------
# Panneau de Filtres Exécutif (Disposition sur 2 lignes)
# ---------------------------------------------------------
st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
st.markdown(f"<div style='font-weight: 700; color: {COLOR_DARK_TEXT}; font-size: 1.0rem; margin-bottom: 12px;'>🔍 Filtres Dynamiques de l'Analyse</div>", unsafe_allow_html=True)

col_f1, col_f2 = st.columns(2)

with col_f1:
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 6px;">
        <span>🏢</span>
        <span style="font-weight: 600; color: {COLOR_PRIMARY_BLUE}; font-size: 0.9rem;">Agences / Zones :</span>
    </div>
    """, unsafe_allow_html=True)
    selected_zones = st.pills(
        "Filtrer par agence",
        options=zones,
        default=zones,
        selection_mode="multi",
        label_visibility="collapsed"
    ) if zones else []

with col_f2:
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 6px;">
        <span>📅</span>
        <span style="font-weight: 600; color: {COLOR_PRIMARY_BLUE}; font-size: 0.9rem;">Années d'exercice :</span>
    </div>
    """, unsafe_allow_html=True)
    selected_years = st.pills(
        "Filtrer par année",
        options=years,
        default=years,
        selection_mode="multi",
        label_visibility="collapsed"
    ) if years else []

st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

st.markdown(f"""
<div style="display: flex; align-items: center; gap: 6px; margin-bottom: 6px;">
    <span>📆</span>
    <span style="font-weight: 600; color: {COLOR_PRIMARY_BLUE}; font-size: 0.9rem;">Mois (Sélection multiple) :</span>
</div>
""", unsafe_allow_html=True)

mois_keys = list(MOIS_DICT.keys())
selected_mois = st.pills(
    "Filtrer par mois",
    options=mois_keys,
    format_func=lambda x: MOIS_DICT[x],
    default=mois_keys,
    selection_mode="multi",
    label_visibility="collapsed"
)

st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# Construction dynamique des clauses WHERE SQL (Zones, Années, Mois)
# ---------------------------------------------------------
all_zones_selected = len(selected_zones) == len(zones) or len(selected_zones) == 0
all_years_selected = len(selected_years) == len(years) or len(selected_years) == 0
all_mois_selected = len(selected_mois) == len(MOIS_DICT) or len(selected_mois) == 0

def build_where_clause(table_alias, include_zone=True, include_date=True):
    conds = []
    if include_zone and not all_zones_selected:
        zone_list_str = ", ".join([f"'{z}'" for z in selected_zones])
        if table_alias == 'cot':
            conds.append(f"cot.zone IN ({zone_list_str})")
        elif table_alias == 'c':
            conds.append(f"c.zone IN ({zone_list_str})")
        else:
            conds.append(f"{table_alias}.zone IN ({zone_list_str})")
            
    if include_date:
        date_col = "cot.daterecucotisation" if table_alias == 'cot' else f"{table_alias}.date_d_admission"
        
        if not all_years_selected:
            year_list_str = ", ".join([f"'{y}'" for y in selected_years])
            conds.append(f"TO_CHAR(CAST({date_col} AS DATE), 'YYYY') IN ({year_list_str})")
            
        if not all_mois_selected:
            mois_list_str = ", ".join([f"'{m}'" for m in selected_mois])
            conds.append(f"TO_CHAR(CAST({date_col} AS DATE), 'MM') IN ({mois_list_str})")
            
    return ("WHERE " + " AND ".join(conds)) if conds else ""

where_zone_s = build_where_clause('s', True, True)
where_zone_c = build_where_clause('c', True, False)
where_zone_cot = build_where_clause('cot', True, True)

# ---------------------------------------------------------
# Récupération & Calculs des Métriques pour les 5 Cartes KPI
# ---------------------------------------------------------
nb_membres, tot_cotis, tot_rembourse, nb_sinistres = 0, 0.0, 0.0, 0

with engine.connect() as conn:
    try:
        query_membres = f"SELECT COUNT(DISTINCT m.code_membre) FROM dim_membre m JOIN dim_contrat c ON m.contrat = c.contrat {where_zone_c};" if not all_zones_selected else "SELECT COUNT(DISTINCT code_membre) FROM dim_membre;"
        nb_membres = conn.execute(text(query_membres)).scalar() or 0
    except Exception: pass

    try:
        tot_cotis = float(conn.execute(text(f"SELECT COALESCE(SUM(cot.montant_cotisation_payee), 0) FROM fact_cotisation cot {where_zone_cot};")).scalar() or 0.0)
    except Exception: pass

    try:
        tot_rembourse = float(conn.execute(text(f"SELECT COALESCE(SUM(s.montant_rembourse), 0) FROM fact_sinistre s {where_zone_s};")).scalar() or 0.0)
    except Exception: pass

    try:
        nb_sinistres = conn.execute(text(f"SELECT COUNT(DISTINCT s.sinistre) FROM fact_sinistre s {where_zone_s};")).scalar() or 0
    except Exception: pass

ratio_sp = (tot_rembourse / tot_cotis * 100) if tot_cotis > 0 else 0.0

# ---------------------------------------------------------
# Bandeau Supérieur : Alignement des 5 Cartes KPI (Style Dashboard)
# ---------------------------------------------------------
k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown(f"""
    <div class="kpi-card kpi-blue">
        <div class="kpi-header">
            <span class="kpi-title">Membres</span>
            <div class="kpi-icon" style="background:#E0F2FE; color:{COLOR_PRIMARY_BLUE};">👥</div>
        </div>
        <div class="kpi-value">{nb_membres:,}</div>
        <span class="kpi-badge badge-neutral">Portefeuille actif</span>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card kpi-green">
        <div class="kpi-header">
            <span class="kpi-title">Cotisations</span>
            <div class="kpi-icon" style="background:#DCFCE7; color:{COLOR_SECONDARY_GREEN};">💰</div>
        </div>
        <div class="kpi-value" style="font-size:1.15rem;">{tot_cotis:,.0f} <span style="font-size:0.75rem; font-weight:normal;">Ar</span></div>
        <span class="kpi-badge badge-success">Recettes globales</span>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card kpi-orange">
        <div class="kpi-header">
            <span class="kpi-title">Remboursements</span>
            <div class="kpi-icon" style="background:#FEF3C7; color:#D97706;">🏥</div>
        </div>
        <div class="kpi-value" style="font-size:1.15rem;">{tot_rembourse:,.0f} <span style="font-size:0.75rem; font-weight:normal;">Ar</span></div>
        <span class="kpi-badge badge-neutral">Charges prestations</span>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-card kpi-purple">
        <div class="kpi-header">
            <span class="kpi-title">Dossiers / Sinistres</span>
            <div class="kpi-icon" style="background:#EEF2FF; color:#6366F1;">📋</div>
        </div>
        <div class="kpi-value">{nb_sinistres:,}</div>
        <span class="kpi-badge badge-neutral">Dossiers traités</span>
    </div>
    """, unsafe_allow_html=True)

with k5:
    status_class = "badge-danger" if ratio_sp > 80 else "badge-success"
    status_text = "⚠️ Risque Élevé" if ratio_sp > 80 else "✅ Maîtrisé"
    card_color = "kpi-red" if ratio_sp > 80 else "kpi-green"
    
    st.markdown(f"""
    <div class="kpi-card {card_color}">
        <div class="kpi-header">
            <span class="kpi-title">Ratio S / P</span>
            <div class="kpi-icon" style="background:#FEE2E2; color:#DC2626;">📊</div>
        </div>
        <div class="kpi-value">{ratio_sp:.1f} %</div>
        <span class="kpi-badge {status_class}">{status_text}</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 1. Grille des Plafonds & Respect des Règles de Prise en Charge
# ---------------------------------------------------------
st.markdown("""
<div class="section-header">
    <span class="section-title-text">📋 1. Analyse du Respect des Plafonds par Type de Soin</span>
    <div class="section-line"></div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="info-barème-card">
    <span style="font-weight: 700; color: {COLOR_PRIMARY_BLUE};">Barème de Garantie Mutuelle SAHI :</span><br>
    • <b>Soins Primaires</b> : Plafond <b>10 000 Ar</b> &nbsp;|&nbsp; 
    • <b>Petite Chirurgie / Obs. Médicale / Accouchement Simple</b> : Plafond <b>50 000 Ar</b><br>
    • <b>Hospitalisation Médicale</b> : Plafond <b>140 000 Ar</b> &nbsp;|&nbsp; 
    • <b>Cas Chirurgical / Césarienne</b> : Plafond <b>300 000 Ar</b><br>
    • <b>Plafond Annuel Individuel</b> : <b>400 000 Ar</b> / an / personne
</div>
""", unsafe_allow_html=True)

query_plafonds = f"""
    SELECT 
        COALESCE(s.type_de_prise_en_charge, 'Non Spécifié') AS "Type de Soin",
        COUNT(DISTINCT s.sinistre) AS "Nombre de Cas",
        SUM(s.montant_des_soins) AS "Frais de Soins Engagés (Ar)",
        SUM(s.montant_rembourse) AS "Total Remboursé (Ar)",
        SUM(s.montant_des_soins - s.montant_rembourse) AS "Reste à Charge Membres (Ar)",
        ROUND(AVG(s.montant_rembourse)::numeric, 2) AS "Moyenne Remboursée (Ar)",
        MAX(s.montant_rembourse) AS "Max Remboursé Effectif (Ar)"
    FROM fact_sinistre s
    {where_zone_s}
    GROUP BY s.type_de_prise_en_charge
    ORDER BY "Total Remboursé (Ar)" DESC;
"""

try:
    df_plafonds = pd.read_sql(text(query_plafonds), engine)
    
    col_pl1, col_pl2 = st.columns([6, 4])
    
    with col_pl1:
        st.dataframe(
            df_plafonds.style.format({
                "Frais de Soins Engagés (Ar)": "{:,.2f}",
                "Total Remboursé (Ar)": "{:,.2f}",
                "Reste à Charge Membres (Ar)": "{:,.2f}",
                "Moyenne Remboursée (Ar)": "{:,.2f}",
                "Max Remboursé Effectif (Ar)": "{:,.0f}"
            }),
            use_container_width=True
        )

    with col_pl2:
        if not df_plafonds.empty:
            fig_pl = px.bar(
                df_plafonds,
                x="Type de Soin",
                y=["Total Remboursé (Ar)", "Reste à Charge Membres (Ar)"],
                title="Prise en Charge Mutuelle vs Reste à Charge",
                barmode="stack",
                color_discrete_map={
                    "Total Remboursé (Ar)": COLOR_SECONDARY_GREEN, 
                    "Reste à Charge Membres (Ar)": COLOR_PRIMARY_BLUE
                },
                template="plotly_white"
            )
            fig_pl.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig_pl, use_container_width=True)

except Exception as e:
    st.error(f"Erreur chargement des plafonds : {e}")

# ---------------------------------------------------------
# 2. Suivi du Plafond Annuel Individuel (400 000 Ar / an)
# ---------------------------------------------------------
st.markdown("""
<div class="section-header">
    <span class="section-title-text">👤 2. Consommation du Plafond Annuel Individuel (Max 400 000 Ar)</span>
    <div class="section-line"></div>
</div>
""", unsafe_allow_html=True)

query_cumul_annuel = f"""
    SELECT 
        s.code_membre AS "Code Membre",
        s.nom || ' ' || s.prenom AS "Nom & Prénom",
        TO_CHAR(CAST(s.date_d_admission AS DATE), 'YYYY') AS "Année",
        COUNT(DISTINCT s.sinistre) AS "Nombre Sinistres",
        SUM(s.montant_des_soins) AS "Cumul Soins (Ar)",
        SUM(s.montant_rembourse) AS "Cumul Remboursé (Ar)",
        400000 - SUM(s.montant_rembourse) AS "Solde Plafond Annuel (Ar)",
        ROUND((SUM(s.montant_rembourse) / 400000.0 * 100)::numeric, 1) AS "Taux d'Épuisement (%)"
    FROM fact_sinistre s
    {where_zone_s}
    GROUP BY s.code_membre, s.nom, s.prenom, TO_CHAR(CAST(s.date_d_admission AS DATE), 'YYYY')
    HAVING SUM(s.montant_rembourse) >= 200000
    ORDER BY "Cumul Remboursé (Ar)" DESC;
"""

try:
    df_cumul = pd.read_sql(text(query_cumul_annuel), engine)
    st.markdown(f"<span style='color:{COLOR_MUTED_TEXT}; font-weight:600; font-size:0.9rem;'>Membres Ayant Consommé ≥ 50% de Leur Plafond Annuel (≥ 200 000 Ar)</span>", unsafe_allow_html=True)
    
    st.dataframe(
        df_cumul.style.format({
            "Cumul Soins (Ar)": "{:,.2f}",
            "Cumul Remboursé (Ar)": "{:,.2f}",
            "Solde Plafond Annuel (Ar)": "{:,.2f}",
            "Taux d'Épuisement (%)": "{:.1f} %"
        }),
        use_container_width=True
    )

except Exception as e:
    st.error(f"Erreur calcul plafond annuel : {e}")

# ---------------------------------------------------------
# 3. Analyse par Groupe de Pathologies
# ---------------------------------------------------------
st.markdown("""
<div class="section-header">
    <span class="section-title-text">🩸 3. Analyse par Groupe de Pathologies</span>
    <div class="section-line"></div>
</div>
""", unsafe_allow_html=True)

query_patho = f"""
    SELECT 
        COALESCE(s.groupe_de_pathologie, 'Non précisé') AS "Pathologie",
        COUNT(DISTINCT s.sinistre) AS "Nombre de cas",
        SUM(s.montant_des_soins) AS "Frais de Soins Total (Ar)",
        SUM(s.montant_rembourse) AS "Montant Remboursé Total (Ar)",
        ROUND(AVG(s.montant_rembourse)::numeric, 2) AS "Coût Moyen Remboursé (Ar)"
    FROM fact_sinistre s
    {where_zone_s}
    GROUP BY s.groupe_de_pathologie
    ORDER BY "Montant Remboursé Total (Ar)" DESC;
"""

try:
    df_patho = pd.read_sql(text(query_patho), engine)
    col_patho_tbl, col_patho_chart = st.columns([6, 4])

    with col_patho_tbl:
        st.dataframe(
            df_patho.style.format({
                "Frais de Soins Total (Ar)": "{:,.2f}",
                "Montant Remboursé Total (Ar)": "{:,.2f}",
                "Coût Moyen Remboursé (Ar)": "{:,.2f}"
            }),
            use_container_width=True
        )

    with col_patho_chart:
        if not df_patho.empty:
            df_top7_patho = df_patho.sort_values("Coût Moyen Remboursé (Ar)", ascending=False).head(7)
            fig_patho = px.bar(
                df_top7_patho,
                x="Coût Moyen Remboursé (Ar)",
                y="Pathologie",
                orientation="h",
                title="Top 7 Pathologies par Coût Moyen Remboursé",
                color="Coût Moyen Remboursé (Ar)",
                color_continuous_scale=[[0, '#E0F2FE'], [1, COLOR_PRIMARY_BLUE]],
                template="plotly_white"
            )
            fig_patho.update_layout(yaxis={'categoryorder': 'total ascending'}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig_patho, use_container_width=True)
except Exception as e:
    st.error(f"Erreur lors du chargement des pathologies : {e}")

# ---------------------------------------------------------
# 4. Analyse par Prestataire de Soins
# ---------------------------------------------------------
st.markdown("""
<div class="section-header">
    <span class="section-title-text">🏥 4. Analyse par Prestataire de Soins</span>
    <div class="section-line"></div>
</div>
""", unsafe_allow_html=True)

query_prest = f"""
    SELECT 
        COALESCE(s.prestataire_de_sante, 'Non Spécifié') AS "Prestataire",
        COALESCE(s.public_prive, 'Non Précisé') AS "Secteur",
        COUNT(DISTINCT s.sinistre) AS "Nombre de prestations",
        SUM(s.montant_des_soins) AS "Total Frais Soins (Ar)",
        SUM(s.montant_rembourse) AS "Total Remboursé (Ar)",
        ROUND(AVG(s.montant_rembourse)::numeric, 2) AS "Remboursement Moyen (Ar)"
    FROM fact_sinistre s
    {where_zone_s}
    GROUP BY s.prestataire_de_sante, s.public_prive
    ORDER BY "Total Remboursé (Ar)" DESC
    LIMIT 15;
"""

try:
    df_prest = pd.read_sql(text(query_prest), engine)
    st.dataframe(
        df_prest.style.format({
            "Total Frais Soins (Ar)": "{:,.2f}",
            "Total Remboursé (Ar)": "{:,.2f}",
            "Remboursement Moyen (Ar)": "{:,.2f}"
        }),
        use_container_width=True
    )
except Exception as e:
    st.error(f"Erreur lors du chargement des prestataires : {e}")

# ---------------------------------------------------------
# 5. Analyse par Secteur Public vs Privé
# ---------------------------------------------------------
st.markdown("""
<div class="section-header">
    <span class="section-title-text">⚖️ 5. Analyse par Secteur (Public vs Privé)</span>
    <div class="section-line"></div>
</div>
""", unsafe_allow_html=True)

query_secteur = f"""
    SELECT 
        COALESCE(s.public_prive, 'Non Spécifié') AS "Secteur",
        COUNT(DISTINCT s.sinistre) AS "Nombre de soins",
        SUM(s.montant_des_soins) AS "Frais de Soins Totaux (Ar)",
        SUM(s.montant_rembourse) AS "Total Remboursé (Ar)",
        ROUND(AVG(s.montant_des_soins)::numeric, 2) AS "Coût Moyen par Soin (Ar)",
        ROUND(AVG(s.montant_rembourse)::numeric, 2) AS "Remboursement Moyen (Ar)"
    FROM fact_sinistre s
    {where_zone_s}
    GROUP BY s.public_prive
    ORDER BY "Total Remboursé (Ar)" DESC;
"""

try:
    df_secteur = pd.read_sql(text(query_secteur), engine)
    col_sec1, col_sec2 = st.columns(2)

    with col_sec1:
        st.markdown(f"<span style='color:{COLOR_MUTED_TEXT}; font-weight:600; font-size:0.9rem;'>Synthèse des Soins par Secteur</span>", unsafe_allow_html=True)
        st.dataframe(
            df_secteur.style.format({
                "Frais de Soins Totaux (Ar)": "{:,.2f}",
                "Total Remboursé (Ar)": "{:,.2f}",
                "Coût Moyen par Soin (Ar)": "{:,.2f}",
                "Remboursement Moyen (Ar)": "{:,.2f}"
            }),
            use_container_width=True
        )

    with col_sec2:
        if not df_secteur.empty:
            fig_sec = px.bar(
                df_secteur,
                x="Secteur",
                y=["Coût Moyen par Soin (Ar)", "Remboursement Moyen (Ar)"],
                barmode="group",
                title="Coût Moyen vs Remboursement Moyen par Secteur",
                labels={"value": "Montant (Ar)", "variable": "Indicateur"},
                color_discrete_map={
                    "Coût Moyen par Soin (Ar)": COLOR_PRIMARY_BLUE,
                    "Remboursement Moyen (Ar)": COLOR_SECONDARY_GREEN
                },
                template="plotly_white"
            )
            fig_sec.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig_sec, use_container_width=True)
except Exception as e:
    st.error(f"Erreur lors de l'analyse par secteur : {e}")

# ---------------------------------------------------------
# 6. Scoring de Risque Médico-Financier par Contrat (Phase 15)
# ---------------------------------------------------------
st.markdown("""
<div class="section-header">
    <span class="section-title-text">⚠️ 6. Scoring de Risque Médico-Financier par Contrat (Phase 15)</span>
    <div class="section-line"></div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="info-barème-card">
    <span style="font-weight: 700; color: #0F172A;">Méthodologie d'Évaluation du Risque :</span><br>
    Évaluation du risque de déséquilibre financier des contrats basée sur la Cotisation Dûe (Barème Forfaitaire) et 3 critères actuariels :<br>
    1. <b>Ratio Sinistre / Prime (S/P)</b> (Poids: 50%) — Remboursements ÷ Cotisation Dûe<br>
    2. <b>Fréquence des sollicitations</b> (Poids: 30%)<br>
    3. <b>Consommation du plafond annuel</b> (Poids: 20%)
</div>
""", unsafe_allow_html=True)

query_risk_data = f"""
    WITH cotis_contrat AS (
        SELECT 
            cot.contrat,
            SUM(cot.montant_cotisation_payee) AS total_cotisations_payees
        FROM fact_cotisation cot
        {where_zone_cot}
        GROUP BY cot.contrat
    ),
    sinistres_contrat AS (
        SELECT 
            s.contrat,
            COUNT(DISTINCT s.sinistre) AS n_sinistres,
            SUM(s.montant_rembourse) AS total_rembourse,
            SUM(s.montant_des_soins) AS total_soins
        FROM fact_sinistre s
        {where_zone_s}
        GROUP BY s.contrat
    )
    SELECT 
        c.contrat AS "Contrat",
        c.zone AS "Zone",
        c.produit AS "Produit",
        COALESCE(c.montant_total_de_cotisation_a_collecter_sur_ce_contrat, 0) AS "Cotisation Dûe (Ar)",
        COALESCE(cot.total_cotisations_payees, 0) AS "Cotisations Encaissées (Ar)",
        COALESCE(sin.n_sinistres, 0) AS "Nombre Sinistres",
        COALESCE(sin.total_soins, 0) AS "Frais Soins Engagés (Ar)",
        COALESCE(sin.total_rembourse, 0) AS "Remboursements Total (Ar)"
    FROM dim_contrat c
    LEFT JOIN cotis_contrat cot ON c.contrat = cot.contrat
    LEFT JOIN sinistres_contrat sin ON c.contrat = sin.contrat
    {where_zone_c};
"""

try:
    df_risk = pd.read_sql(text(query_risk_data), engine)

    if not df_risk.empty:
        df_risk["Ratio S/P"] = df_risk.apply(
            lambda r: r["Remboursements Total (Ar)"] / r["Cotisation Dûe (Ar)"] if r["Cotisation Dûe (Ar)"] > 0 
            else (5.0 if r["Remboursements Total (Ar)"] > 0 else 0.0), axis=1
        )

        df_risk["Score_SP"] = df_risk["Ratio S/P"].apply(lambda x: min((x / 1.5) * 100, 100))
        df_risk["Score_Freq"] = df_risk["Nombre Sinistres"].apply(lambda x: min((x / 3.0) * 100, 100))
        df_risk["Score_Plafond"] = df_risk["Remboursements Total (Ar)"].apply(lambda x: min((x / 400000.0) * 100, 100))

        df_risk["Score de Risque"] = (
            0.50 * df_risk["Score_SP"] + 
            0.30 * df_risk["Score_Freq"] + 
            0.20 * df_risk["Score_Plafond"]
        ).round(1)

        def get_risk_category(score):
            if score < 30:
                return "1 - Faible (Rentable)"
            elif score < 60:
                return "2 - Modéré (Équilibré)"
            else:
                return "3 - Élevé (Déficitaire)"

        df_risk["Niveau de Risque"] = df_risk["Score de Risque"].apply(get_risk_category)

        # KPIs Risque
        rk1, rk2, rk3, rk4 = st.columns(4)
        total_contrats = len(df_risk)
        nb_eleve = (df_risk["Niveau de Risque"] == "3 - Élevé (Déficitaire)").sum()
        nb_modere = (df_risk["Niveau de Risque"] == "2 - Modéré (Équilibré)").sum()
        nb_faible = (df_risk["Niveau de Risque"] == "1 - Faible (Rentable)").sum()

        rk1.metric("Contrats Traités", f"{total_contrats:,}")
        rk2.metric("Risque Élevé", f"{nb_eleve:,}", delta=f"{(nb_eleve/total_contrats*100 if total_contrats > 0 else 0):.1f}%", delta_color="inverse")
        rk3.metric("Risque Modéré", f"{nb_modere:,}")
        rk4.metric("Risque Faible", f"{nb_faible:,}")

        # Graphiques Risque harmonisés
        col_rk_graph1, col_rk_graph2 = st.columns(2)

        with col_rk_graph1:
            fig_risk_pie = px.pie(
                df_risk, names="Niveau de Risque", title="Distribution du Risque Financier des Contrats",
                color="Niveau de Risque",
                color_discrete_map={
                    "1 - Faible (Rentable)": COLOR_SECONDARY_GREEN, 
                    "2 - Modéré (Équilibré)": COLOR_PRIMARY_BLUE, 
                    "3 - Élevé (Déficitaire)": "#EF4444"
                },
                hole=0.4,
                template="plotly_white"
            )
            fig_risk_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig_risk_pie, use_container_width=True)

        with col_rk_graph2:
            df_risk_plot = df_risk[df_risk["Score de Risque"] > 0].copy()
            df_risk_plot["Taille_Bulle"] = df_risk_plot["Score de Risque"].apply(lambda x: max(x, 5.0))

            fig_risk_scatter = px.scatter(
                df_risk_plot,
                x="Cotisation Dûe (Ar)",
                y="Remboursements Total (Ar)",
                size="Taille_Bulle",
                color="Niveau de Risque",
                hover_name="Contrat",
                hover_data={
                    "Cotisation Dûe (Ar)": ":,.0f",
                    "Cotisations Encaissées (Ar)": ":,.0f",
                    "Remboursements Total (Ar)": ":,.0f",
                    "Score de Risque": ":.1f",
                    "Nombre Sinistres": True,
                    "Taille_Bulle": False
                },
                title="Remboursement vs Cotisation Dûe (Taille = Score de Risque)",
                color_discrete_map={
                    "1 - Faible (Rentable)": COLOR_SECONDARY_GREEN, 
                    "2 - Modéré (Équilibré)": COLOR_PRIMARY_BLUE, 
                    "3 - Élevé (Déficitaire)": "#EF4444"
                },
                template="plotly_white"
            )
            fig_risk_scatter.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig_risk_scatter, use_container_width=True)

        st.markdown(f"<span style='color:{COLOR_DARK_TEXT}; font-weight:700; font-size:1.05rem;'>🚨 Liste des Contrats Déficitaires à Suivre</span>", unsafe_allow_html=True)
        
        df_deficitaires = df_risk[df_risk["Niveau de Risque"] == "3 - Élevé (Déficitaire)"].sort_values("Score de Risque", ascending=False)[
            ["Contrat", "Zone", "Produit", "Cotisation Dûe (Ar)", "Cotisations Encaissées (Ar)", "Nombre Sinistres", "Frais Soins Engagés (Ar)", "Remboursements Total (Ar)", "Ratio S/P", "Score de Risque"]
        ]
        
        if not df_deficitaires.empty:
            csv_data = df_deficitaires.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Exporter la liste des contrats déficitaires (CSV)",
                data=csv_data,
                file_name="contrats_deficitaires_sahi.csv",
                mime="text/csv"
            )

        st.dataframe(
            df_deficitaires.style.format({
                "Cotisation Dûe (Ar)": "{:,.0f}",
                "Cotisations Encaissées (Ar)": "{:,.0f}",
                "Frais Soins Engagés (Ar)": "{:,.0f}",
                "Remboursements Total (Ar)": "{:,.0f}",
                "Ratio S/P": "{:.2f}",
                "Score de Risque": "{:.1f}"
            }),
            use_container_width=True
        )

except Exception as e:
    st.error(f"Erreur scoring de risque : {e}")
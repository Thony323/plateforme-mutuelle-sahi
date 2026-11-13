import sys
from pathlib import Path

# Résolution du chemin racine du projet
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------
# Configuration de la page Streamlit
# ---------------------------------------------------------
st.set_page_config(
    page_title="Dashboard Général - Mutuelle SAHI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Connexion native à la base de données Neon (Corrigée)
# ---------------------------------------------------------
@st.cache_resource
def get_db_connection():
    # URL de connexion Neon explicite pour s'assurer que Streamlit cible la bonne base
    DATABASE_URL = "postgresql://neondb_owner:npg_qinVJeSZmW45@ep-super-poetry-bahmteh8-pooler.c-8.eu-central-1.aws.neon.tech/neondb?sslmode=require"
    return st.connection("sql", type="sql", url=DATABASE_URL)

conn = get_db_connection()

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
# Custom CSS Style "Executive Board" & Sélecteur d'Agence
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

    /* Panneau de sélection des Agences (Style Boutons Modernes) */
    .agency-filter-container {{
        background: {COLOR_CARD_BG};
        border-radius: 14px;
        padding: 16px 22px;
        border: 1px solid #E2E8F0;
        border-left: 6px solid {COLOR_PRIMARY_BLUE};
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.03);
        margin-bottom: 25px;
        display: flex;
        align-items: center;
        gap: 15px;
    }}

    /* Cartes KPI Élégantes */
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

    /* Titres de Section */
    .section-header {{
        display: flex;
        align-items: center;
        gap: 10px;
        margin-top: 30px;
        margin-bottom: 16px;
    }}
    .section-title-text {{
        font-size: 1.2rem;
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
    st.info("Utilisez ce menu pour explorer les modules d'analyse médico-financière et de pilotage du risque.")

# ---------------------------------------------------------
# En-tête Principal
# ---------------------------------------------------------
st.markdown("""
<div class="dashboard-header">
    <div>
        <div class="dashboard-header-title">🏥 Dashboard Général — Mutuelle SAHI</div>
        <div class="dashboard-header-sub">Système de pilotage du risque médico-financier et de suivi de la performance.</div>
    </div>
    <div class="status-badge">🟢 Base de données connectée</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Chargement et Sélection des Agences (Zones)
# ---------------------------------------------------------
@st.cache_data(ttl=600)
def load_zones():
    try:
        df = conn.query("SELECT DISTINCT zone FROM dim_contrat WHERE zone IS NOT NULL AND zone != '' ORDER BY zone;", ttl=600)
        return df['zone'].tolist()
    except Exception as e:
        st.error(f"Erreur lors du chargement des agences : {e}")
        return []

zones = load_zones()

# Design épuré sous forme de bandeau de sélection d'agences
st.markdown('<div class="agency-filter-container">', unsafe_allow_html=True)
col_lbl, col_sel = st.columns([1, 4])
with col_lbl:
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 8px;">
        <span style="font-size: 1.1rem;">🏢</span>
        <span style="font-weight: 700; color: {COLOR_PRIMARY_BLUE}; font-size: 0.95rem;">Agences / Zones :</span>
    </div>
    """, unsafe_allow_html=True)
with col_sel:
    selected_zones = st.pills(
        "Filtrer par agence",
        options=zones,
        default=zones,
        selection_mode="multi",
        label_visibility="collapsed"
    ) if zones else []
st.markdown('</div>', unsafe_allow_html=True)

# Construction sécurisée des clauses WHERE SQL
all_zones_selected = len(selected_zones) == len(zones) or len(selected_zones) == 0

if not all_zones_selected:
    zone_list_str = ", ".join([f"'{z}'" for z in selected_zones])
    where_zone_c = f"WHERE c.zone IN ({zone_list_str})"
    where_zone_cot = f"WHERE cot.zone IN ({zone_list_str})"
    where_zone_s = f"WHERE s.zone IN ({zone_list_str})"
else:
    where_zone_c = ""
    where_zone_cot = ""
    where_zone_s = ""

# ---------------------------------------------------------
# Récupération & Calculs des Métriques
# ---------------------------------------------------------
nb_membres, tot_cotis, tot_rembourse, nb_sinistres = 0, 0.0, 0.0, 0

try:
    query_membres = f"SELECT COUNT(DISTINCT m.code_membre) FROM dim_membre m JOIN dim_contrat c ON m.contrat = c.contrat {where_zone_c};" if not all_zones_selected else "SELECT COUNT(DISTINCT code_membre) FROM dim_membre;"
    res = conn.query(query_membres, ttl=600)
    nb_membres = int(res.iloc[0, 0]) if not res.empty else 0
except Exception: pass

try:
    res = conn.query(f"SELECT COALESCE(SUM(cot.montant_cotisation_payee), 0) FROM fact_cotisation cot {where_zone_cot};", ttl=600)
    tot_cotis = float(res.iloc[0, 0]) if not res.empty else 0.0
except Exception: pass

try:
    res = conn.query(f"SELECT COALESCE(SUM(s.montant_rembourse), 0) FROM fact_sinistre s {where_zone_s};", ttl=600)
    tot_rembourse = float(res.iloc[0, 0]) if not res.empty else 0.0
except Exception: pass

try:
    res = conn.query(f"SELECT COUNT(DISTINCT s.sinistre) FROM fact_sinistre s {where_zone_s};", ttl=600)
    nb_sinistres = int(res.iloc[0, 0]) if not res.empty else 0
except Exception: pass

# Calcul du ratio Sinistres / Cotisations (S/P)
ratio_sp = (tot_rembourse / tot_cotis * 100) if tot_cotis > 0 else 0.0

# ---------------------------------------------------------
# Bandeau Supérieur : Alignement des 5 Cartes KPI
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
        <div class="kpi-value" style="font-size:1.2rem;">{tot_cotis:,.0f} <span style="font-size:0.75rem; font-weight:normal;">Ar</span></div>
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
        <div class="kpi-value" style="font-size:1.2rem;">{tot_rembourse:,.0f} <span style="font-size:0.75rem; font-weight:normal;">Ar</span></div>
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

# ---------------------------------------------------------
# Évolution Temporelle
# ---------------------------------------------------------
st.markdown("""
<div class="section-header">
    <span class="section-title-text">📈 Évolution Financière & Dynamique des Sinistres</span>
    <div class="section-line"></div>
</div>
""", unsafe_allow_html=True)

c_evo1, c_evo2 = st.columns(2)

with c_evo1:
    query_evo_fin = f"""
        WITH cotisations_mois AS (
            SELECT SUBSTRING(cot.moiscouvertversement FROM 1 FOR 7) AS mois, SUM(cot.montant_cotisation_payee) AS total_cotisation
            FROM fact_cotisation cot {where_zone_cot} GROUP BY SUBSTRING(cot.moiscouvertversement FROM 1 FOR 7)
        ),
        sinistres_mois AS (
            SELECT TO_CHAR(CAST(s.date_d_admission AS DATE), 'YYYY-MM') AS mois, SUM(s.montant_rembourse) AS total_rembourse
            FROM fact_sinistre s {where_zone_s} GROUP BY TO_CHAR(CAST(s.date_d_admission AS DATE), 'YYYY-MM')
        )
        SELECT COALESCE(c.mois, s.mois) AS mois, COALESCE(c.total_cotisation, 0) AS cotisations, COALESCE(s.total_rembourse, 0) AS remboursements
        FROM cotisations_mois c FULL OUTER JOIN sinistres_mois s ON c.mois = s.mois
        WHERE COALESCE(c.mois, s.mois) IS NOT NULL AND COALESCE(c.mois, s.mois) != '' ORDER BY mois;
    """
    try:
        df_evo_fin = conn.query(query_evo_fin, ttl=600)
        if not df_evo_fin.empty:
            fig_fin = go.Figure()
            fig_fin.add_trace(go.Scatter(
                x=df_evo_fin['mois'], y=df_evo_fin['cotisations'], name='Cotisations',
                line=dict(color=COLOR_SECONDARY_GREEN, width=3, shape='spline'),
                fill='tonexty', fillcolor='rgba(26, 168, 67, 0.05)'
            ))
            fig_fin.add_trace(go.Scatter(
                x=df_evo_fin['mois'], y=df_evo_fin['remboursements'], name='Prestations',
                line=dict(color='#EF4444', width=3, shape='spline')
            ))
            fig_fin.update_layout(
                title=dict(text="<b>Cotisations vs Prestations (Ar)</b>", font=dict(size=14, color=COLOR_DARK_TEXT)),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=10, r=10, t=40, b=10),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#F1F5F9')
            )
            st.plotly_chart(fig_fin, use_container_width=True)
        else: st.info("Aucune donnée financière disponible.")
    except Exception as e: st.warning(f"Erreur : {e}")

with c_evo2:
    query_evo_sin = f"""
        SELECT TO_CHAR(CAST(s.date_d_admission AS DATE), 'YYYY-MM') AS mois, COUNT(DISTINCT s.sinistre) AS nb_sinistres
        FROM fact_sinistre s {where_zone_s} GROUP BY TO_CHAR(CAST(s.date_d_admission AS DATE), 'YYYY-MM') ORDER BY mois;
    """
    try:
        df_evo_sin = conn.query(query_evo_sin, ttl=600)
        if not df_evo_sin.empty:
            fig_sin = px.bar(
                df_evo_sin, x='mois', y='nb_sinistres',
                color_discrete_sequence=[COLOR_PRIMARY_BLUE], text_auto=True
            )
            fig_sin.update_traces(opacity=0.9)
            fig_sin.update_layout(
                title=dict(text="<b>Volume Mensuel de Sinistres</b>", font=dict(size=14, color=COLOR_DARK_TEXT)),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=10, r=10, t=40, b=10),
                xaxis=dict(title="", showgrid=False), yaxis=dict(title="", showgrid=True, gridcolor='#F1F5F9')
            )
            st.plotly_chart(fig_sin, use_container_width=True)
        else: st.info("Aucune donnée disponible.")
    except Exception as e: st.warning(f"Erreur : {e}")

# ---------------------------------------------------------
# Répartition & Cartographie
# ---------------------------------------------------------
st.markdown("""
<div class="section-header">
    <span class="section-title-text">📊 Répartition des Charges & Analyse Géographique</span>
    <div class="section-line"></div>
</div>
""", unsafe_allow_html=True)

c_rep1, c_rep2 = st.columns(2)

with c_rep1:
    query_patho = f"""
        SELECT COALESCE(s.groupe_de_pathologie, 'Non précisé') AS groupe_pathologie, SUM(s.montant_rembourse) AS total_rembourse
        FROM fact_sinistre s {where_zone_s} GROUP BY s.groupe_de_pathologie ORDER BY total_rembourse DESC LIMIT 7;
    """
    try:
        df_patho = conn.query(query_patho, ttl=600)
        if not df_patho.empty:
            palette = [COLOR_PRIMARY_BLUE, COLOR_SECONDARY_GREEN, '#38BDF8', '#818CF8', '#F59E0B', '#10B981', '#64748B']
            fig_pie = px.pie(
                df_patho, names='groupe_pathologie', values='total_rembourse',
                hole=0.6, color_discrete_sequence=palette
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(
                title=dict(text="<b>Top Pathologies par Remboursement</b>", font=dict(size=14, color=COLOR_DARK_TEXT)),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                showlegend=False, margin=dict(l=10, r=10, t=40, b=10)
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else: st.info("Aucune donnée disponible.")
    except Exception as e: st.warning(f"Erreur : {e}")

with c_rep2:
    query_zone = f"""
        SELECT COALESCE(cot.zone, 'Non Renseigné') AS zone, SUM(cot.montant_cotisation_payee) AS total_cotisation
        FROM fact_cotisation cot {where_zone_cot} GROUP BY cot.zone ORDER BY total_cotisation DESC;
    """
    try:
        df_zone = conn.query(query_zone, ttl=600)
        if not df_zone.empty:
            fig_zone = px.bar(
                df_zone, x='total_cotisation', y='zone', orientation='h', text_auto='.2s',
                color='total_cotisation', color_continuous_scale=['#E0F2FE', COLOR_PRIMARY_BLUE]
            )
            fig_zone.update_layout(
                title=dict(text="<b>Cotisations Collectées par Zone (Ar)</b>", font=dict(size=14, color=COLOR_DARK_TEXT)),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                coloraxis_showscale=False, margin=dict(l=10, r=10, t=40, b=10),
                xaxis=dict(title="", showgrid=True, gridcolor='#F1F5F9'), yaxis=dict(title="", autorange="reversed")
            )
            st.plotly_chart(fig_zone, use_container_width=True)
        else: st.info("Aucune donnée géographique disponible.")
    except Exception as e: st.warning(f"Erreur : {e}")
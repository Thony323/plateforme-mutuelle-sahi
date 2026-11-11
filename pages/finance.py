import sys
from pathlib import Path

# 1. Résolution du chemin racine du projet EN PREMIER (avant les imports personnalisés)
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import text, inspect
from database.connection import get_engine

st.set_page_config(
    page_title="Analyse Financière - Mutuelle SAHI", 
    page_icon="💰", 
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
    .filter-panel {{
        background: {COLOR_CARD_BG};
        border-radius: 14px;
        padding: 20px 24px;
        border: 1px solid #E2E8F0;
        border-left: 6px solid {COLOR_PRIMARY_BLUE};
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.03);
        margin-bottom: 25px;
    }}
    div[data-testid="stPills"] {{
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 6px !important;
    }}

    /* Cartes KPI Élégantes (Harmonisées avec sante.py) */
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

# En-tête principal
st.markdown("""
<div class="dashboard-header">
    <div>
        <div class="dashboard-header-title">💰 Analyse Financière & Actuarielle - Mutuelle SAHI</div>
        <div class="dashboard-header-sub">Pilotage des plafonds de garantie, maîtrise des charges de santé et équilibre médico-financier.</div>
    </div>
    <div class="status-badge">🟢 Base PostgreSQL Connectée</div>
</div>
""", unsafe_allow_html=True)

# Plafonds métier officiels de la mutuelle SAHI
PLAFONDS_PRISES_EN_CHARGE = {
    'soins primaires': 10000,
    'observation': 50000,
    'petite chirurgie': 50000,
    'accouchement simple': 50000,
    'accouchement difficile': 50000,
    'accouchement césarienne': 300000,
    'hospitalisation médicale': 140000,
    'hospitalisation chirurgicale': 300000
}

@st.cache_data(ttl=300)
def load_data_from_db():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if "fact_sinistre" not in tables:
        raise Exception("La table `fact_sinistre` est introuvable dans la base de données PostgreSQL.")
    
    columns = [col['name'] for col in inspector.get_columns("fact_sinistre")]
    
    col_sinistre = 'sinistre_id' if 'sinistre_id' in columns else ('sinistre' if 'sinistre' in columns else columns[0])
    col_contrat = 'contrat_id' if 'contrat_id' in columns else ('contrat' if 'contrat' in columns else None)
    col_membre = 'code_membre' if 'code_membre' in columns else ('membre_id' if 'membre_id' in columns else None)
    col_date = 'date_d_admission' if 'date_d_admission' in columns else ('date_recu' if 'date_recu' in columns else ('date_admission' if 'date_admission' in columns else None))
    
    col_type_pec = None
    for candidate in ['type_de_prise_en_charge', 'type_prise_en_charge', 'groupe_de_pathologie', 'groupe_pathologie', 'prestation']:
        if candidate in columns:
            col_type_pec = candidate
            break

    col_soins = 'montant_des_soins' if 'montant_des_soins' in columns else ('montant_soins' if 'montant_soins' in columns else 'montant')
    col_rembourse = 'montant_rembourse' if 'montant_rembourse' in columns else 'rembourse'
    col_reste = 'reste_a_charge' if 'reste_a_charge' in columns else ('montant_reste_charge' if 'montant_reste_charge' in columns else 'reste')

    select_fields = [f"s.{col_sinistre} AS sinistre_id"]
    select_fields.append(f"s.{col_contrat} AS contrat_id" if col_contrat else "'N/A' AS contrat_id")
    select_fields.append(f"s.{col_membre} AS code_membre" if col_membre else "'N/A' AS code_membre")
    select_fields.append(f"s.{col_date} AS date_recu" if col_date else "NULL AS date_recu")
    
    if col_type_pec:
        select_fields.append(f"COALESCE(s.{col_type_pec}, 'Soins primaires') AS type_prise_en_charge")
    else:
        select_fields.append("'Soins primaires' AS type_prise_en_charge")
        
    select_fields.append(f"COALESCE(s.{col_soins}, 0) AS montant_soins")
    select_fields.append(f"COALESCE(s.{col_rembourse}, 0) AS montant_rembourse" if col_rembourse in columns else "0 AS montant_rembourse")
    select_fields.append(f"COALESCE(s.{col_reste}, 0) AS montant_reste_charge" if col_reste in columns else "0 AS montant_reste_charge")

    has_dim_contrat = "dim_contrat" in tables and col_contrat
    if has_dim_contrat:
        contrat_cols = [c['name'] for c in inspector.get_columns("dim_contrat")]
        zone_col = 'zone' if 'zone' in contrat_cols else contrat_cols[0]
        select_fields.append(f"c.{zone_col} AS zone")
        query = f"SELECT {', '.join(select_fields)} FROM fact_sinistre s LEFT JOIN dim_contrat c ON s.{col_contrat} = c.{col_contrat};"
    else:
        select_fields.append("'Non spécifié' AS zone")
        query = f"SELECT {', '.join(select_fields)} FROM fact_sinistre s;"

    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn)
    return df

try:
    df_raw = load_data_from_db()

    if df_raw.empty:
        st.warning("⚠️ Aucune donnée n'a été trouvée dans la base de données pour cette période.")
    else:
        if 'date_recu' in df_raw.columns:
            df_raw['date_recu_dt'] = pd.to_datetime(df_raw['date_recu'], errors='coerce')
            df_raw['annee'] = df_raw['date_recu_dt'].dt.strftime('%Y').fillna('2026')
            df_raw['mois'] = df_raw['date_recu_dt'].dt.strftime('%m').fillna('01')
        else:
            df_raw['annee'] = '2026'
            df_raw['mois'] = '01'

        zones_list = df_raw['zone'].dropna().unique().tolist() if 'zone' in df_raw.columns else []
        years_list = sorted(df_raw['annee'].dropna().unique().tolist(), reverse=True)

        MOIS_DICT = {
            "01": "Janvier", "02": "Février", "03": "Mars", "04": "Avril",
            "05": "Mai", "06": "Juin", "07": "Juillet", "08": "Août",
            "09": "Septembre", "10": "Octobre", "11": "Novembre", "12": "Décembre"
        }

        # Panneau de filtres exécutif sur 2 lignes
        st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
        st.markdown(f"<div style='font-weight: 700; color: {COLOR_DARK_TEXT}; font-size: 1.0rem; margin-bottom: 12px;'>🔍 Filtres Dynamiques de l'Analyse Financière</div>", unsafe_allow_html=True)
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            selected_zones = st.pills("Agences / Zones", options=zones_list, default=zones_list, selection_mode="multi") if zones_list else []
        with col_f2:
            selected_years = st.pills("Années", options=years_list, default=years_list, selection_mode="multi") if years_list else []

        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        mois_keys = list(MOIS_DICT.keys())
        selected_mois = st.pills("Mois (Sélection multiple)", options=mois_keys, format_func=lambda x: MOIS_DICT[x], default=mois_keys, selection_mode="multi")
        st.markdown('</div>', unsafe_allow_html=True)

        # Filtrage du DataFrame en Python
        df_filtered = df_raw.copy()
        if selected_zones and len(selected_zones) < len(zones_list):
            df_filtered = df_filtered[df_filtered['zone'].isin(selected_zones)]
        if selected_years and len(selected_years) < len(years_list):
            df_filtered = df_filtered[df_filtered['annee'].isin(selected_years)]
        if selected_mois and len(selected_mois) < len(mois_keys):
            df_filtered = df_filtered[df_filtered['mois'].isin(selected_mois)]

        # Application des Plafonds Métier SAHI avec correspondance large
        def calculer_plafond_acte(type_pec):
            val = str(type_pec).lower().strip()
            for key, plafond in PLAFONDS_PRISES_EN_CHARGE.items():
                if key in val:
                    return plafond
            return 10000  # Valeur par défaut

        df_filtered['plafond_acte'] = df_filtered['type_prise_en_charge'].apply(calculer_plafond_acte)
        
        # ALIGNEMENT : Utilisation directe du montant remboursé officiel de la base de données
        df_filtered['remboursement_accorde'] = df_filtered['montant_rembourse']
        
        df_filtered['depassement_plafond'] = (df_filtered['montant_soins'] - df_filtered['plafond_acte']).clip(lower=0)
        df_filtered['reste_a_charge_membre'] = df_filtered['montant_soins'] - df_filtered['remboursement_accorde']

        def statut_pec(row):
            if row['montant_soins'] <= row['plafond_acte']:
                return "Prise en Charge Totale (100%)"
            return "Prise en Charge Partielle (Plafond Dépassé)"

        df_filtered['statut_prise_en_charge'] = df_filtered.apply(statut_pec, axis=1)

        # ---------------------------------------------------------
        # KPIs Actuariels Clés (Design aligné sur sante.py)
        # ---------------------------------------------------------
        total_soins = df_filtered['montant_soins'].sum()
        total_rembourse = df_filtered['remboursement_accorde'].sum()
        total_reste_charge = df_filtered['reste_a_charge_membre'].sum()
        nb_depassements = (df_filtered['depassement_plafond'] > 0).sum()
        taux_couverture_moyen = (total_rembourse / total_soins * 100) if total_soins > 0 else 0.0

        k1, k2, k3, k4, k5 = st.columns(5)

        with k1:
            st.markdown(f"""
            <div class="kpi-card kpi-blue">
                <div class="kpi-header">
                    <span class="kpi-title">Frais de Soins</span>
                    <div class="kpi-icon" style="background:#E0F2FE; color:{COLOR_PRIMARY_BLUE};">💰</div>
                </div>
                <div class="kpi-value" style="font-size:1.1rem;">{total_soins:,.0f} <span style="font-size:0.75rem; font-weight:normal;">Ar</span></div>
                <span class="kpi-badge badge-neutral">Engagements totaux</span>
            </div>
            """, unsafe_allow_html=True)

        with k2:
            st.markdown(f"""
            <div class="kpi-card kpi-green">
                <div class="kpi-header">
                    <span class="kpi-title">Total Remboursé</span>
                    <div class="kpi-icon" style="background:#DCFCE7; color:{COLOR_SECONDARY_GREEN};">🤝</div>
                </div>
                <div class="kpi-value" style="font-size:1.1rem;">{total_rembourse:,.0f} <span style="font-size:0.75rem; font-weight:normal;">Ar</span></div>
                <span class="kpi-badge badge-success">Charges mutuelle</span>
            </div>
            """, unsafe_allow_html=True)

        with k3:
            st.markdown(f"""
            <div class="kpi-card kpi-orange">
                <div class="kpi-header">
                    <span class="kpi-title">Reste à Charge</span>
                    <div class="kpi-icon" style="background:#FEF3C7; color:#D97706;">👤</div>
                </div>
                <div class="kpi-value" style="font-size:1.1rem;">{total_reste_charge:,.0f} <span style="font-size:0.75rem; font-weight:normal;">Ar</span></div>
                <span class="kpi-badge badge-neutral">Part adhérents</span>
            </div>
            """, unsafe_allow_html=True)

        with k4:
            st.markdown(f"""
            <div class="kpi-card kpi-purple">
                <div class="kpi-header">
                    <span class="kpi-title">Taux de Couverture</span>
                    <div class="kpi-icon" style="background:#EEF2FF; color:#6366F1;">📈</div>
                </div>
                <div class="kpi-value">{taux_couverture_moyen:.1f} %</div>
                <span class="kpi-badge badge-neutral">Moyen global</span>
            </div>
            """, unsafe_allow_html=True)

        with k5:
            card_color = "kpi-red" if nb_depassements > 0 else "kpi-green"
            badge_class = "badge-danger" if nb_depassements > 0 else "badge-success"
            badge_text = "⚠️ Attention" if nb_depassements > 0 else "✅ Conforme"

            st.markdown(f"""
            <div class="kpi-card {card_color}">
                <div class="kpi-header">
                    <span class="kpi-title">Dépassements</span>
                    <div class="kpi-icon" style="background:#FEE2E2; color:#DC2626;">⚠️</div>
                </div>
                <div class="kpi-value">{nb_depassements:,}</div>
                <span class="kpi-badge {badge_class}">{badge_text}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ---------------------------------------------------------
        # Graphiques d'Analyse pour le Jury M2
        # ---------------------------------------------------------
        g1, g2 = st.columns(2)

        with g1:
            st.markdown("""
            <div class="section-header">
                <span class="section-title-text">📊 Remboursements vs Reste à Charge par Type de Soin</span>
                <div class="section-line"></div>
            </div>
            """, unsafe_allow_html=True)
            df_grouped = df_filtered.groupby('type_prise_en_charge')[
                ['remboursement_accorde', 'reste_a_charge_membre']
            ].sum().reset_index()

            fig_bar = px.bar(
                df_grouped,
                x='type_prise_en_charge',
                y=['remboursement_accorde', 'reste_a_charge_membre'],
                labels={'value': 'Montant (Ar)', 'type_prise_en_charge': 'Type de Soin', 'variable': 'Indicateur'},
                barmode='stack',
                color_discrete_map={'remboursement_accorde': COLOR_SECONDARY_GREEN, 'reste_a_charge_membre': COLOR_PRIMARY_BLUE},
                template='plotly_white'
            )
            fig_bar.update_layout(xaxis_tickangle=-25, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_bar, use_container_width=True)

        with g2:
            st.markdown("""
            <div class="section-header">
                <span class="section-title-text">🍩 Proportion du Respect des Plafonds</span>
                <div class="section-line"></div>
            </div>
            """, unsafe_allow_html=True)
            fig_pie = px.pie(
                df_filtered,
                names='statut_prise_en_charge',
                color='statut_prise_en_charge',
                color_discrete_map={
                    "Prise en Charge Totale (100%)": COLOR_SECONDARY_GREEN,
                    "Prise en Charge Partielle (Plafond Dépassé)": "#EF4444"
                },
                hole=0.4,
                template='plotly_white'
            )
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_pie, use_container_width=True)

        # Graphiques analytiques avancés
        g3, g4 = st.columns(2)

        with g3:
            st.markdown("""
            <div class="section-header">
                <span class="section-title-text">📈 Évolution Mensuelle des Charges de Santé</span>
                <div class="section-line"></div>
            </div>
            """, unsafe_allow_html=True)
            if 'date_recu_dt' in df_filtered.columns and not df_filtered['date_recu_dt'].isna().all():
                df_time = df_filtered.groupby(df_filtered['date_recu_dt'].dt.to_period('M'))[['montant_soins', 'remboursement_accorde']].sum().reset_index()
                df_time['periode'] = df_time['date_recu_dt'].astype(str)
                
                fig_time = px.line(
                    df_time, x='periode', y=['montant_soins', 'remboursement_accorde'],
                    markers=True, title="Tendance chronologique des engagements financiers",
                    labels={'value': 'Montant (Ar)', 'periode': 'Mois'},
                    color_discrete_sequence=[COLOR_PRIMARY_BLUE, COLOR_SECONDARY_GREEN],
                    template='plotly_white'
                )
                fig_time.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_time, use_container_width=True)
            else:
                st.info("Données chronologiques insuffisantes pour l'analyse temporelle.")

        with g4:
            st.markdown("""
            <div class="section-header">
                <span class="section-title-text">📍 Exposition Financière par Zone / Agence</span>
                <div class="section-line"></div>
            </div>
            """, unsafe_allow_html=True)
            if 'zone' in df_filtered.columns:
                df_zone = df_filtered.groupby('zone')[['montant_soins', 'remboursement_accorde']].sum().reset_index()
                fig_zone = px.bar(
                    df_zone, x='zone', y=['montant_soins', 'remboursement_accorde'],
                    barmode='group', title="Comparatif par antenne (Fianarantsoa, Manakara, Ambositra...)",
                    labels={'value': 'Montant (Ar)', 'zone': 'Zone géographique'},
                    color_discrete_sequence=[COLOR_PRIMARY_BLUE, COLOR_SECONDARY_GREEN],
                    template='plotly_white'
                )
                fig_zone.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_zone, use_container_width=True)
            else:
                st.info("Données géographiques non disponibles.")

        # ---------------------------------------------------------
        # Tableau Détaillé & Export Professionnel
        # ---------------------------------------------------------
        st.markdown("""
        <div class="section-header">
            <span class="section-title-text">📋 Relevé Détaillé et Contrôle des Plafonds de Soins</span>
            <div class="section-line"></div>
        </div>
        """, unsafe_allow_html=True)

        cols_a_afficher = [
            'sinistre_id', 'code_membre', 'zone', 'type_prise_en_charge', 
            'montant_soins', 'plafond_acte', 'remboursement_accorde', 
            'depassement_plafond', 'reste_a_charge_membre', 'statut_prise_en_charge'
        ]
        cols_disponibles = [c for c in cols_a_afficher if c in df_filtered.columns]
        
        # Dictionnaire des nouveaux noms de colonnes pour l'affichage (Métier)
        noms_colonnes_affichage = {
            'sinistre_id': 'ID Sinistre',
            'code_membre': 'Code Membre',
            'zone': 'Zone / Agence',
            'type_prise_en_charge': 'Type de Soin',
            'montant_soins': 'Frais de Soins',
            'plafond_acte': 'Plafond Barème',
            'remboursement_accorde': 'Montant Remboursé',
            'depassement_plafond': 'Dépassement Plafond',
            'reste_a_charge_membre': 'Reste à Charge',
            'statut_prise_en_charge': 'Statut Prise en Charge'
        }
        
        # Renommer les colonnes d'un DataFrame temporaire pour l'affichage
        df_display = df_filtered[cols_disponibles].rename(columns=noms_colonnes_affichage)

        # Export CSV avec les nouveaux noms de colonnes
        csv_data = df_display.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Exporter le rapport d'analyse financière (CSV)",
            data=csv_data,
            file_name="analyse_financiere_sahi.csv",
            mime="text/csv"
        )

        # Affichage Streamlit avec le formatage mis à jour
        st.dataframe(
            df_display.sort_values(by='Dépassement Plafond', ascending=False).style.format({
                "Frais de Soins": "{:,.0f} Ar",
                "Plafond Barème": "{:,.0f} Ar",
                "Montant Remboursé": "{:,.0f} Ar",
                "Dépassement Plafond": "{:,.0f} Ar",
                "Reste à Charge": "{:,.0f} Ar"
            }),
            use_container_width=True
        )

except Exception as e:
    st.error(f"⚠️ Erreur lors du chargement des données depuis PostgreSQL : {e}")
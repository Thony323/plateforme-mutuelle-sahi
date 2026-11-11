import sys
from pathlib import Path

# Résolution du chemin vers la racine du projet
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text
from database.connection import get_engine

st.set_page_config(page_title="Audit Détaillé des Reçus - SAHI", page_icon="🧾", layout="wide")

st.title("🧾 Audit Détaillé des Reçus & Postes de Dépenses (Niveau Micro)")
st.markdown("Analyse fine des pièces comptables, de la structure des coûts de santé, des restes à charge et détection d'anomalies.")

engine = get_engine()

# ---------------------------------------------------------
# Sidebar - Filtres par Zone
# ---------------------------------------------------------
st.sidebar.header("🔍 Filtres Globaux")

@st.cache_data(ttl=600)
def load_zones():
    try:
        with engine.connect() as conn:
            df = pd.read_sql(text("SELECT DISTINCT zone FROM dim_contrat WHERE zone IS NOT NULL AND zone != '' ORDER BY zone;"), conn)
            return df['zone'].tolist()
    except Exception:
        return []

zones = load_zones()
selected_zones = st.sidebar.multiselect("Sélectionner la / les Zone(s) :", options=zones, default=zones) if zones else []

all_zones_selected = len(selected_zones) == len(zones) or len(selected_zones) == 0

if not all_zones_selected:
    zone_list_str = ", ".join([f"'{z}'" for z in selected_zones])
    where_zone_rs = f"WHERE rs.zone IN ({zone_list_str})"
else:
    where_zone_rs = ""

# ---------------------------------------------------------
# Bandeau KPIs Synthèse Reçus
# ---------------------------------------------------------
try:
    with engine.connect() as conn:
        q_kpi = f"""
            SELECT 
                COUNT(rs.recu) AS total_recus,
                COALESCE(SUM(rs.montant_des_soins), 0) AS total_soins,
                COALESCE(SUM(rs.montant_rembourse), 0) AS total_rembourse,
                COALESCE(SUM(rs.montant_restant_a_charge), 0) AS total_reste_charge
            FROM fact_recu_sinistre rs
            {where_zone_rs};
        """
        row_kpi = conn.execute(text(q_kpi)).fetchone()
        
        tot_recus = row_kpi[0] or 0
        tot_soins = float(row_kpi[1] or 0.0)
        tot_remb = float(row_kpi[2] or 0.0)
        tot_rac = float(row_kpi[3] or 0.0)

        taux_couverture = (tot_remb / tot_soins * 100) if tot_soins > 0 else 0.0

        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("Nombre Total de Reçus", f"{tot_recus:,}")
        k2.metric("Montant Total Soins", f"{tot_soins:,.0f} Ar")
        k3.metric("Total Remboursé", f"{tot_remb:,.0f} Ar")
        k4.metric("Reste à Charge Patient", f"{tot_rac:,.0f} Ar")
        k5.metric("Taux de Prise en Charge", f"{taux_couverture:.1f} %")

except Exception as e:
    st.error(f"Erreur chargement KPIs Reçus : {e}")

st.divider()

# ---------------------------------------------------------
# 1. Ventilation des Dépenses par Poste (Médicaments, Actes, etc.)
# ---------------------------------------------------------
st.header("💊 1. Structure des Coûts par Type de Dépense")

query_poste = f"""
    SELECT 
        COALESCE(rs.type_de_depense, 'Non Spécifié') AS "Type de Dépense",
        COUNT(rs.recu) AS "Nombre de Reçus",
        SUM(rs.montant_des_soins) AS "Frais de Soins (Ar)",
        SUM(rs.montant_rembourse) AS "Montant Remboursé (Ar)",
        SUM(rs.montant_restant_a_charge) AS "Reste à Charge (Ar)",
        ROUND(AVG(rs.montant_des_soins)::numeric, 2) AS "Coût Moyen par Reçu (Ar)"
    FROM fact_recu_sinistre rs
    {where_zone_rs}
    GROUP BY rs.type_de_depense
    ORDER BY "Frais de Soins (Ar)" DESC;
"""

try:
    df_poste = pd.read_sql(text(query_poste), engine)
    
    col_p1, col_p2 = st.columns([6, 4])

    with col_p1:
        st.dataframe(
            df_poste.style.format({
                "Frais de Soins (Ar)": "{:,.2f}",
                "Montant Remboursé (Ar)": "{:,.2f}",
                "Reste à Charge (Ar)": "{:,.2f}",
                "Coût Moyen par Reçu (Ar)": "{:,.2f}"
            }),
            use_container_width=True
        )

    with col_p2:
        if not df_poste.empty:
            fig_poste = px.pie(
                df_poste,
                names="Type de Dépense",
                values="Frais de Soins (Ar)",
                title="Part des Dépenses de Santé par Poste",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Dark24
            )
            st.plotly_chart(fig_poste, use_container_width=True)

except Exception as e:
    st.error(f"Erreur analyse par poste : {e}")

st.divider()

# ---------------------------------------------------------
# 2. Analyse des Motifs de Plafonnement / Non-Remboursement
# ---------------------------------------------------------
st.header("📊 2. Analyse des Motifs de Dépassement / Non-Remboursement (`reasoncharge`)")

query_reason = f"""
    SELECT 
        COALESCE(rs.reasoncharge, 'Prise en charge à 100%') AS "Motif de Limite",
        COUNT(rs.recu) AS "Nombre de Factures Concernées",
        SUM(rs.montant_des_soins) AS "Montant Soins (Ar)",
        SUM(rs.montant_rembourse) AS "Montant Remboursé (Ar)",
        SUM(rs.montant_restant_a_charge) AS "Reste à Charge Incombé (Ar)"
    FROM fact_recu_sinistre rs
    {where_zone_rs}
    GROUP BY rs.reasoncharge
    ORDER BY "Reste à Charge Incombé (Ar)" DESC;
"""

try:
    df_reason = pd.read_sql(text(query_reason), engine)
    
    col_r1, col_r2 = st.columns(2)

    with col_r1:
        st.subheader("Synthèse par Motif de Limitation")
        st.dataframe(
            df_reason.style.format({
                "Montant Soins (Ar)": "{:,.2f}",
                "Montant Remboursé (Ar)": "{:,.2f}",
                "Reste à Charge Incombé (Ar)": "{:,.2f}"
            }),
            use_container_width=True
        )

    with col_r2:
        if not df_reason.empty:
            fig_reason = px.bar(
                df_reason,
                x="Motif de Limite",
                y="Reste à Charge Incombé (Ar)",
                text_auto='.2s',
                title="Reste à Charge Généré par Motif de Limitation",
                color="Reste à Charge Incombé (Ar)",
                color_continuous_scale="Oranges"
            )
            st.plotly_chart(fig_reason, use_container_width=True)

except Exception as e:
    st.error(f"Erreur analyse motifs de charge : {e}")

st.divider()

# ---------------------------------------------------------
# 3. Détection d'Anomalies / Audit des Factures Élevées
# ---------------------------------------------------------
st.header("🔍 3. Audit des Factures Atypiques / Montants Élevés")
st.markdown("Identification des reçus individuels présentant un coût des soins particulièrement élevé ou un fort reste à charge.")

seuil_montant = st.slider("Filtrer les reçus dont les soins dépassent (Ar) :", min_value=100000, max_value=2000000, value=500000, step=100000)

query_anomalies = f"""
    SELECT 
        rs.sinistre AS "Code Sinistre",
        rs.recu AS "Code Reçu",
        rs.nom || ' ' || rs.prenom AS "Bénéficiaire",
        rs.type_de_depense AS "Type Dépense",
        COALESCE(rs.prestataire_de_sante, 'Non Spécifié') AS "Prestataire",
        rs.montant_des_soins AS "Montant Soins (Ar)",
        rs.montant_rembourse AS "Montant Remboursé (Ar)",
        rs.montant_restant_a_charge AS "Reste à Charge (Ar)",
        COALESCE(rs.reasoncharge, 'Sans dépassement') AS "Motif Charge"
    FROM fact_recu_sinistre rs
    WHERE rs.montant_des_soins >= {seuil_montant}
    {'AND rs.zone IN (' + ",".join([f"'{z}'" for z in selected_zones]) + ')' if not all_zones_selected else ''}
    ORDER BY rs.montant_des_soins DESC;
"""

try:
    df_anomalies = pd.read_sql(text(query_anomalies), engine)
    st.info(f"**{len(df_anomalies)}** reçu(s) trouvé(s) dépassant **{seuil_montant:,.0f} Ar**.")
    
    st.dataframe(
        df_anomalies.style.format({
            "Montant Soins (Ar)": "{:,.2f}",
            "Montant Remboursé (Ar)": "{:,.2f}",
            "Reste à Charge (Ar)": "{:,.2f}"
        }),
        use_container_width=True
    )

except Exception as e:
    st.error(f"Erreur détection d'anomalies : {e}")

st.divider()

# ---------------------------------------------------------
# 4. Moteur de Recherche des Reçus d'Adhérents
# ---------------------------------------------------------
st.header("🔎 4. Moteur de Recherche des Reçus d'Adhérents")

search_term = st.text_input("Rechercher un numéro de reçu / nom de membre / code contrat :", "")

if search_term:
    query_search = f"""
        SELECT 
            rs.recu AS "N° Reçu",
            rs.sinistre AS "N° Sinistre",
            rs.contrat AS "Contrat",
            rs.nom || ' ' || rs.prenom AS "Adhérent / Patient",
            rs.type_de_depense AS "Poste Soin",
            COALESCE(rs.prestataire_de_sante, 'Non Spécifié') AS "Établissement",
            rs.montant_des_soins AS "Facture Soin (Ar)",
            rs.montant_rembourse AS "Remboursé (Ar)",
            rs.montant_restant_a_charge AS "Reste à Charge (Ar)",
            COALESCE(rs.reasoncharge, 'Prise en charge 100%') AS "Motif Limitation"
        FROM fact_recu_sinistre rs
        WHERE LOWER(rs.recu) LIKE LOWER('%{search_term}%')
           OR LOWER(rs.nom) LIKE LOWER('%{search_term}%')
           OR LOWER(rs.contrat) LIKE LOWER('%{search_term}%')
        ORDER BY rs.montant_des_soins DESC;
    """
    try:
        df_search = pd.read_sql(text(query_search), engine)
        st.info(f"**{len(df_search)}** résultat(s) trouvé(s).")
        st.dataframe(
            df_search.style.format({
                "Facture Soin (Ar)": "{:,.2f}",
                "Remboursé (Ar)": "{:,.2f}",
                "Reste à Charge (Ar)": "{:,.2f}"
            }),
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Erreur recherche reçu : {e}")
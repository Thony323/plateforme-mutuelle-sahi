import sys
from pathlib import Path
import os
import re
import calendar

# Résolution du chemin racine du projet (PROJET_MS)
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd
from sqlalchemy import text
from database.connection import get_engine

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

st.set_page_config(page_title="Assistant Intelligent - Mutuelle SAHI", page_icon="🤖", layout="wide")

st.title("🤖 Assistant Intelligent & Analytique (Mutuelle SAHI)")
st.markdown("""
Posez vos questions sur la base de données de la Mutuelle SAHI. L'assistant explore toutes vos tables pour vous répondre avec précision.
""")

engine = get_engine()

# ---------------------------------------------------------
# 1. Schéma Compact et Essentiel
# ---------------------------------------------------------
CORTEX_SCHEMA = """
Tables PostgreSQL Mutuelle SAHI :
- fact_cotisation (federation, ong, branch, zone, communaute, produit, code_annexe, contrat, montant_cotisation_payee, moiscouvertversement, daterecucotisation)
- fact_sinistre (federation, ong, branch, zone, communaute, sinistre, produit, contrat, code_annexe, code_membre, sexe, nom, prenom, date_d_admission, groupe_de_pathologie, prestataire_de_sante, montant_des_soins, montant_rembourse)
- dim_contrat (federation, ong, branch, zone, communaute, produit, contrat, nom, prenom, telephone, date_d_adhesion, montant_total_de_cotisation_a_collecter_sur_ce_contrat, montant_total_rembourse_sur_ce_contrat)
- dim_membre (federation, ong, branch, zone, communaute, produit, contrat, code_membre, sexe, date_de_naissance, nom, prenom, type_de_membre)
"""

# ---------------------------------------------------------
# 2. Configuration Groq Sécurisée
# ---------------------------------------------------------
api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key) if (GROQ_AVAILABLE and api_key) else None

@st.cache_data(ttl=1800)
def get_safe_groq_model():
    if not client:
        return None
    try:
        models = client.models.list()
        model_ids = [m.id for m in models.data if hasattr(m, 'id')]
        preferred = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "llama3-70b-8192", "llama3-8b-8192"]
        for p in preferred:
            if p in model_ids:
                return p
        for m in model_ids:
            if "llama" in m.lower() and not any(bad in m.lower() for bad in ["audio", "arabic", "canopylabs", "orpheus"]):
                return m
        return "llama3-70b-8192"
    except Exception:
        return "llama3-70b-8192"

ACTIVE_MODEL = get_safe_groq_model()

def execute_sql_safely(sql_query: str):
    with engine.connect() as conn:
        df = pd.read_sql(text(sql_query), conn)
    return df

# ---------------------------------------------------------
# 3. Moteur Avancé et Flexible (Règles Métier + IA)
# ---------------------------------------------------------
def parse_date_filters(question: str):
    q = question.lower()
    mois_dict = {
        "janvier": "01", "février": "02", "fevrier": "02", "mars": "03", "avril": "04",
        "mai": "05", "juin": "06", "juillet": "07", "août": "08", "aout": "08",
        "septembre": "09", "octobre": "10", "novembre": "11", "décembre": "12", "decembre": "12"
    }
    found_month = None
    for m_name, m_num in mois_dict.items():
        if m_name in q:
            found_month = m_num
            break
    year_match = re.search(r'20\d{2}', q)
    found_year = year_match.group(0) if year_match else "2026"
    
    if found_month:
        last_day = calendar.monthrange(int(found_year), int(found_month))[1]
        start_date = f"{found_year}-{found_month}-01"
        end_date = f"{found_year}-{found_month}-{last_day:02d}"
        return start_date, end_date, f"{found_month}/{found_year}"
    return None, None, "global"

def run_hybrid_engine(user_question: str, chat_history: list):
    q = user_question.lower()
    start_date, end_date, period_label = parse_date_filters(q)
    
    try:
        # 1. Gestion élargie des cotisations (mois spécifique ou global)
        if any(k in q for k in ["cotisation", "cotiser", "recette", "perçu"]):
            where_clause = ""
            if start_date:
                # On filtre sur la date de reçu ou le mois couvert selon la présence de la date
                where_clause = f"WHERE daterecucotisation >= '{start_date}' AND daterecucotisation <= '{end_date}'"
            
            sql = f"""
            SELECT 
                COALESCE(SUM(montant_cotisation_payee), 0) AS total_cotisation,
                COUNT(*) AS nombre_recus
            FROM fact_cotisation
            {where_clause}
            """
            df = execute_sql_safely(sql)
            tot = float(df['total_cotisation'].iloc[0]) if not df.empty else 0
            recus = int(df['nombre_recus'].iloc[0]) if not df.empty else 0
            
            msg = f"💰 **Total des Cotisations ({period_label}) :**\n\n- **Montant total :** **{tot:,.0f} Ar**\n- **Nombre de paiements :** `{recus:,}`".replace(',', ' ')
            return msg, df, sql

        # 2. Dépenses / Remboursements sur une période précise
        elif ("depens" in q or "rembours" in q or "sinistre" in q) and start_date:
            sql = f"""
            SELECT 
                COUNT(*) AS nombre_sinistres,
                COALESCE(SUM(montant_rembourse), 0) AS total_rembourse,
                COALESCE(SUM(montant_des_soins), 0) AS total_soins
            FROM fact_sinistre
            WHERE date_d_admission >= '{start_date}' AND date_d_admission <= '{end_date}'
            """
            df = execute_sql_safely(sql)
            tot = float(df['total_rembourse'].iloc[0]) if not df.empty else 0
            msg = f"📊 **Bilan des Sinistres ({period_label}) :**\n\n- **Total Remboursé :** **{tot:,.0f} Ar**\n- **Nombre de sinistres :** `{df['nombre_sinistres'].iloc[0]:,}`".replace(',', ' ')
            return msg, df, sql

        # 3. Pathologies principales
        elif "pathologie" in q or "maladie" in q:
            sql = """
            SELECT groupe_de_pathologie, COUNT(*) AS nombre_cas, SUM(montant_rembourse) AS total_rembourse
            FROM fact_sinistre GROUP BY groupe_de_pathologie ORDER BY total_rembourse DESC LIMIT 5
            """
            df = execute_sql_safely(sql)
            return "🩺 **Top des pathologies par montant de remboursement :**", df, sql

        # 4. Zones et sinistralité
        elif "zone" in q or "sinistralité" in q:
            sql = """
            SELECT zone, COUNT(*) AS nombre_sinistres, SUM(montant_rembourse) AS total_rembourse
            FROM fact_sinistre GROUP BY zone ORDER BY total_rembourse DESC
            """
            df = execute_sql_safely(sql)
            return "📍 **Analyse par zone :**", df, sql

        # 5. Pour toutes les autres questions : Génération IA sécurisée avec Llama
        if client and ACTIVE_MODEL:
            recent_history = chat_history[-4:] if len(chat_history) > 4 else chat_history
            history_str = "\n".join([f"{m['role']}: {m['content']}" for m in recent_history])

            prompt = f"""
            En tant qu'expert SQL PostgreSQL, écris une requête SELECT valide pour répondre à la question ci-dessous en utilisant ces tables :
            {CORTEX_SCHEMA}

            Historique récent :
            {history_str}

            CONSIGNES ABSOLUES :
            1. Renvoie UNIQUEMENT le code SQL SELECT brut (pas de texte, pas de markdown ```).
            2. Utilise COALESCE(SUM(...), 0) pour les totaux.

            Question : {user_question}
            """
            res = client.chat.completions.create(
                model=ACTIVE_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=300
            )
            
            raw_response = res.choices[0].message.content
            sql_query = re.sub(r'```(?:sql)?', '', raw_response, flags=re.IGNORECASE).replace('```', '').strip()
            match = re.search(r'(SELECT[\s\S]+?)(;|\Z)', sql_query, re.IGNORECASE)
            
            if not match or not sql_query.upper().startswith("SELECT"):
                return f"Je n'ai pas pu générer la requête pour cette question spécifique.", None, None
            
            sql_query = match.group(1).strip()
            df_res = execute_sql_safely(sql_query)
            
            if df_res is not None and not df_res.empty:
                synth_res = client.chat.completions.create(
                    model=ACTIVE_MODEL,
                    messages=[{"role": "user", "content": f"Question : '{user_question}'\nRésultats SQL :\n{df_res.to_string(index=False)}\nRédige une réponse claire et professionnelle en français. Formate les montants en Ariary (Ar)."}],
                    temperature=0.1,
                    max_tokens=250
                )
                return synth_res.choices[0].message.content, df_res, sql_query
            else:
                return "Aucun résultat trouvé pour cette demande dans la base de données.", df_res, sql_query

        return "Veuillez configurer votre clé API Groq.", None, None
    except Exception as e:
        return f"Erreur lors de l'exécution SQL : {e}", None, None

# ---------------------------------------------------------
# 4. Interface Streamlit
# ---------------------------------------------------------
st.sidebar.header("💡 Exemples de questions")
exemples = [
    "Donner les cotisations en mai 2026",
    "Combien avons-nous dépensé en juillet 2026 ?",
    "Quelle pathologie représente le plus de dépenses ?",
    "Quelle zone présente le plus de sinistres ?"
]

for ex in exemples:
    if st.sidebar.button(ex):
        st.session_state.prompt_input = ex

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Bonjour ! Posez vos questions sur les cotisations, sinistres, zones ou pathologies de la Mutuelle SAHI."}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Posez votre question...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Analyse des données en cours..."):
            ans_text, df_data, sql_code = run_hybrid_engine(user_input, st.session_state.messages)
            
            st.markdown(ans_text)
            
            if sql_code:
                with st.expander("🔍 Requête SQL exécutée"):
                    st.code(sql_code, language="sql")
            
            if df_data is not None and not df_data.empty:
                with st.expander("📋 Données brutes"):
                    st.dataframe(df_data, use_container_width=True)
                    csv_data = df_data.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Télécharger en CSV",
                        data=csv_data,
                        file_name="resultat_requete.csv",
                        mime="text/csv",
                    )

    st.session_state.messages.append({"role": "assistant", "content": ans_text})
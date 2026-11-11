import streamlit as st

# Configuration globale de l'application
st.set_page_config(
    page_title="Plateforme Décisionnelle - Mutuelle SAHI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Définition de la liste des pages avec leurs chemins exacts depuis la racine
pages = [
    st.Page("pages/dashboard.py", title="Tableau de bord Général", icon="🏠", default=True),
    st.Page("pages/sante.py", title="Analyse Santé", icon="🏥"),
    st.Page("pages/finance.py", title="Analyse Financière", icon="💰"),
    st.Page("pages/risques.py", title="Gestion des Risques", icon="⚠️"),
    st.Page("assistant/chatbot.py", title="Assistant Virtuel / Chatbot", icon="🤖"),
]

# Activation du menu de navigation dans la barre latérale
pg = st.navigation(pages)
pg.run()
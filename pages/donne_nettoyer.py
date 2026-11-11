import os
import pandas as pd
import streamlit as st

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Dashboard Métier - Mutuelle Santé",
    page_icon="📊",
    layout="wide"
)

PROCESSED_DIR = "data/processed"

# Dictionnaire des fichiers nettoyés
FILES = {
    "📋 Dim Contrat": "dim_contrat.csv",
    "👥 Dim Membre": "dim_membre.csv",
    "🔗 Dim Contrat-Membre": "dim_contrat_membre.csv",
    "💰 Fact Cotisation": "fact_cotisation.csv",
    "💵 Fact Recette": "fact_recette.csv",
    "🏥 Fact Sinistre": "fact_sinistre.csv",
    "🧾 Fact Reçu Sinistre": "fact_recu_sinistre.csv"
}

st.title("📊 Exploration des Données Nettoyées - Mutuelle Santé")
st.markdown("Visualisation et contrôle qualité des fichiers CSV dans `data/processed/`")

# Barre latérale (Sidebar) pour naviguer entre les tables
st.sidebar.header("📁 Sélection de la Table")
selected_table_label = st.sidebar.selectbox("Choisissez une table à afficher :", list(FILES.keys()))
file_name = FILES[selected_table_label]
file_path = os.path.join(PROCESSED_DIR, file_name)

if not os.path.exists(file_path):
    st.error(f"❌ Le fichier `{file_name}` est introuvable dans `{PROCESSED_DIR}`. Veuillez exécuter `python src/transform.py` d'abord.")
else:
    # Chargement des données
    @st.cache_data
    def load_data(path):
        return pd.read_csv(path)

    df = load_data(file_path)

    # Affichage des KPIs rapides en haut de page
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Nombre total de lignes", value=f"{len(df):,}")
    with col2:
        st.metric(label="Nombre de colonnes", value=len(df.columns))
    with col3:
        nb_valeurs_manquantes = df.isnull().sum().sum()
        st.metric(label="Valeurs manquantes (NaN)", value=f"{nb_valeurs_manquantes:,}")

    st.markdown("---")

    # Barre de recherche / filtrage interactif
    search_term = st.sidebar.text_input("🔍 Rechercher un mot-clé ou un identifiant (Ex: Contrat, Code membre) :")
    
    if search_term:
        # Filtrer la table sur l'ensemble des colonnes
        mask = df.astype(str).apply(lambda row: row.str.contains(search_term, case=False).any(), axis=1)
        filtered_df = df[mask]
        st.subheader(f"Résultats de la recherche pour : `{search_term}` ({len(filtered_df)} lignes trouvées)")
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.subheader(f"Aperçu des données : {selected_table_label}")
        # Affichage interactif avec pagination, tri et redimensionnement
        st.dataframe(df, use_container_width=True)

    # Analyse rapide des colonnes et types de données
    with st.expander("🛠️ Voir la structure technique des colonnes (Types & Valeurs manquantes)"):
        info_df = pd.DataFrame({
            "Type de donnée": df.dtypes.astype(str),
            "Valeurs Non-Nulle": df.notnull().sum(),
            "Valeurs Manquantes (NaN)": df.isnull().sum(),
            "Exemple de Valeur": df.iloc[0] if len(df) > 0 else None
        })
        st.dataframe(info_df, use_container_width=True)
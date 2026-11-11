import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sqlalchemy import text
from database.connection import get_engine

engine = get_engine()

st.markdown("""
<div class="section-header">
    <span class="section-title-text">👥 7. Segmentation Comportementale par Clustering (K-Means)</span>
    <div class="section-line"></div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<span style='color:#64748B;'>Cette analyse utilise l'apprentissage automatique non-supervisé (K-Means) pour segmenter automatiquement les contrats selon leur profil de consommation de soins, sans seuil prédéfini.</span>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def load_clustering_data():
    query = """
    SELECT 
        s.contrat AS code_contrat,
        c.zone,
        COALESCE(c.produit, 'Non Précisé') AS produit,
        COUNT(DISTINCT s.sinistre) AS nb_sinistres,
        COALESCE(SUM(s.montant_des_soins), 0) AS total_soins,
        COALESCE(SUM(s.montant_rembourse), 0) AS total_rembourse
    FROM fact_sinistre s
    LEFT JOIN dim_contrat c ON s.contrat = c.contrat
    GROUP BY s.contrat, c.zone, c.produit;
    """
    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn)
    return df

df_cluster = load_clustering_data()

if not df_cluster.empty and len(df_cluster) > 5:
    # 1. Sélection des variables pour le clustering
    features = ['nb_sinistres', 'total_soins', 'total_rembourse']
    X = df_cluster[features].fillna(0)

    # 2. Normalisation des données (Standardisation)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 3. Choix du nombre de clusters (ex: k = 3)
    n_clusters = 3
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df_cluster['cluster_id'] = kmeans.fit_predict(X_scaled)

    # Nommer les clusters de manière métier pour le jury
    # On trie par total remboursé moyen pour identifier clairement les profils
    cluster_mapping = {}
    cluster_means = df_cluster.groupby('cluster_id')['total_rembourse'].mean().sort_values()
    cluster_labels = [
        "Profil 1 : Consommateurs Faibles (Sains)",
        "Profil 2 : Consommateurs Modérés (Équilibrés)",
        "Profil 3 : Consommateurs Intensifs (À Risque)"
    ]
    
    for i, cid in enumerate(cluster_means.index):
        cluster_mapping[cid] = cluster_labels[i]
        
    df_cluster['Profil Adhérent'] = df_cluster['cluster_id'].map(cluster_mapping)

    # 4. Affichage des KPIs par Cluster
    col_c1, col_c2, col_c3 = st.columns(3)
    
    summary_cluster = df_cluster.groupby('Profil Adhérent').agg(
        nb_contrats=('code_contrat', 'count'),
        moy_soins=('total_soins', 'mean'),
        moy_remb=('total_rembourse', 'mean')
    ).reset_index()

    # Visualisation interactive en nuage de points (Scatter Plot 3D ou 2D)
    st.markdown("<br>", unsafe_allow_html=True)
    fig_cluster = px.scatter(
        df_cluster,
        x="nb_sinistres",
        y="total_rembourse",
        color="Profil Adhérent",
        size="total_soins",
        hover_name="code_contrat",
        hover_data=["zone", "produit"],
        title="Cartographie des Profils de Consommation (K-Means)",
        labels={"nb_sinistres": "Nombre de Sinistres", "total_rembourse": "Montant Total Remboursé (Ar)"},
        color_discrete_map={
            "Profil 1 : Consommateurs Faibles (Sains)": "#0062BD",       # Bleu SAHI
            "Profil 2 : Consommateurs Modérés (Équilibrés)": "#3B82F6",    # Bleu clair
            "Profil 3 : Consommateurs Intensifs (À Risque)": "#EF4444"   # Rouge alerte
        },
        template="plotly_white"
    )
    fig_cluster.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_cluster, use_container_width=True)

    # Tableau synthétique des profils pour le jury
    st.subheader("📋 Synthèse statistique des profils identifiés par l'IA")
    st.dataframe(
        summary_cluster.style.format({
            "nb_contrats": "{:,}",
            "moy_soins": "{:,.0f} Ar",
            "moy_remb": "{:,.0f} Ar"
        }),
        use_container_width=True
    )
else:
    st.warning("Données insuffisantes pour exécuter le clustering.")
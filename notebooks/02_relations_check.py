import pandas as pd

# Chargement des données
df_contrats = pd.read_excel("data/raw/contrats.xlsx")
df_cotisations = pd.read_excel("data/raw/cotisations.xlsx")
df_sinistres = pd.read_excel("data/raw/sinistres_recu.xlsx")
df_membres = pd.read_excel("data/raw/membres.xlsx")

set_contrats = set(df_contrats['Contrat'])

# Vérification du taux de correspondance des clés
print("=== CONTROLES DE L'INTÉGRITÉ RÉFÉRENTIELLE ===")

cotis_match = set(df_cotisations['Contrat']).issubset(set_contrats)
print(f"1. Clés Cotisations -> Contrats valides : {cotis_match}")

sinistres_match = set(df_sinistres['Contrat']).issubset(set_contrats)
print(f"2. Clés Sinistres -> Contrats valides : {sinistres_match}")

membres_with_contrat = df_membres['Contrat'].isin(set_contrats).mean() * 100
print(f"3. Pourcentage de membres rattachés à un contrat valide : {membres_with_contrat:.2f}%")
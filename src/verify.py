import pandas as pd
import os

PROCESSED_DIR = "data/processed"

print("=" * 80)
print("🔍 VÉRIFICATION DE L'INTÉGRITÉ ET QUALITÉ DES DONNÉES (DATA AUDIT)")
print("=" * 80)

# Chargement des CSV générés
dim_contrat = pd.read_csv(os.path.join(PROCESSED_DIR, "dim_contrat.csv"))
dim_membre = pd.read_csv(os.path.join(PROCESSED_DIR, "dim_membre.csv"))
fact_sinistre = pd.read_csv(os.path.join(PROCESSED_DIR, "fact_sinistre.csv"))
fact_cotisation = pd.read_csv(os.path.join(PROCESSED_DIR, "fact_cotisation.csv"))

# 1. Vérification du nombre de lignes dans dim_membre
print(f"\n1. Nombre total d'enregistrements dans dim_membre : {len(dim_membre)} lignes")
if len(dim_membre) == 16875:
    print("   ✅ VALIDE : L'historique complet des membres et des renouvellements est conservé.")
else:
    print("   ⚠️ ATTENTION : Il manque des enregistrements.")

# 2. Vérification de la clé composite (Clé_Membre_Contrat)
doublons_cle = dim_membre.duplicated(subset=['Clé_Membre_Contrat']).sum()
print(f"\n2. Doublons sur 'Clé_Membre_Contrat' dans dim_membre : {doublons_cle}")
if doublons_cle == 0:
    print("   ✅ VALIDE : La clé primaire composite est unique à 100%.")

# 3. Test de jointure entre Sinistres et Membres (Recherche d'orphelins)
sinistres_orphelins = fact_sinistre[~fact_sinistre['Clé_Membre_Contrat'].isin(dim_membre['Clé_Membre_Contrat'])]
print(f"\n3. Sinistres orphelins (non trouvés dans dim_membre) : {len(sinistres_orphelins)} sur {len(fact_sinistre)}")
if len(sinistres_orphelins) == 0:
    print("   ✅ VALIDE : 100% des sinistres correspondent parfaitement à un membre et un contrat !")

# 4. Vérification des Code Annexe enrichis
null_annexe = dim_membre['Code annexe'].isnull().sum()
print(f"\n4. Code annexe manquants dans dim_membre : {null_annexe}")
if null_annexe == 0:
    print("   ✅ VALIDE : Tous les codes annexes ont été complétés/enrichis.")

print("\n" + "=" * 80)
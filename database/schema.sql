-- Suppression préalable des tables
DROP TABLE IF EXISTS fact_recu_sinistre CASCADE;
DROP TABLE IF EXISTS fact_sinistre CASCADE;
DROP TABLE IF EXISTS fact_recette CASCADE;
DROP TABLE IF EXISTS fact_cotisation CASCADE;
DROP TABLE IF EXISTS dim_contrat_membre CASCADE;
DROP TABLE IF EXISTS dim_membre CASCADE;
DROP TABLE IF EXISTS dim_contrat CASCADE;

-- 1. Dimension Contrat
CREATE TABLE dim_contrat (
    federation TEXT,
    ong TEXT,
    branch TEXT,
    zone TEXT,
    communaute TEXT,
    animateur TEXT,
    animateur2 TEXT,
    produit TEXT,
    contrat TEXT,
    code_annexe TEXT,
    nom TEXT,
    prenom TEXT,
    telephone TEXT,
    date_de_debut_premier_contrat TIMESTAMP,
    date_de_debut_contrat_actuel TIMESTAMP,
    date_de_fin_contrat_actuel TIMESTAMP,
    duree_du_contrat DOUBLE PRECISION,
    date_d_adhesion TIMESTAMP,
    montant_total_de_cotisation_a_collecter_sur_ce_contrat DOUBLE PRECISION,
    montant_du_pret DOUBLE PRECISION,
    afficher_le_pct_de_la_part_fonctionnement DOUBLE PRECISION,
    montant_droit_d_adhesion_sur_ce_contrat_et_cout_d_edition_des_cartes_sur_ce_contrat DOUBLE PRECISION,
    montant_total_collecte_sur_ce_contrat_sans_carte_et_sans_droit_d_adhesion DOUBLE PRECISION,
    montant_total_rembourse_sur_ce_contrat DOUBLE PRECISION,
    date_du_dernier_remboursement TIMESTAMP,
    date_de_saisie TIMESTAMP,
    saisit_par TEXT
);

-- 2. Dimension Membre
CREATE TABLE dim_membre (
    federation TEXT,
    ong TEXT,
    branch TEXT,
    zone TEXT,
    communaute TEXT,
    produit TEXT,
    contrat TEXT,
    code_annexe TEXT,
    code_membre TEXT,
    sexe TEXT,
    date_de_naissance TIMESTAMP,
    nom TEXT,
    prenom TEXT,
    type_de_membre TEXT,
    date_de_debut_premier_contrat TIMESTAMP,
    date_de_debut_dd_mm_yyyy TIMESTAMP,
    date_de_fin_dd_mm_yyyy TIMESTAMP,
    montant_total_rembourse_sur_ce_contrat_pour_cette_personne DOUBLE PRECISION,
    nombre_de_sinistres_rembourses_sur_ce_contrat_pour_cette_personne DOUBLE PRECISION,
    date_du_dernier_remboursement_pour_cette_personne TIMESTAMP,
    date_de_saisie TIMESTAMP,
    cle_membre_contrat TEXT
);

-- 3. Liaison Contrat-Membre
CREATE TABLE dim_contrat_membre (
    federation TEXT,
    ong TEXT,
    branche TEXT,
    zone TEXT,
    communaute TEXT,
    produit TEXT,
    contrat TEXT,
    code_membre TEXT,
    mois DOUBLE PRECISION,
    annee DOUBLE PRECISION,
    cle_membre_contrat TEXT
);

-- 4. Fait Cotisation
CREATE TABLE fact_cotisation (
    federation TEXT,
    ong TEXT,
    branch TEXT,
    zone TEXT,
    communaute TEXT,
    produit TEXT,
    code_annexe TEXT,
    contrat TEXT,
    montant_cotisation_payee DOUBLE PRECISION,
    moiscouvertversement TEXT,
    daterecucotisation TIMESTAMP,
    part_frais_de_fct DOUBLE PRECISION,
    enretard TEXT
);

-- 5. Fait Recette
CREATE TABLE fact_recette (
    federation TEXT,
    ong TEXT,
    branch TEXT,
    zone TEXT,
    communaute TEXT,
    produit TEXT,
    code_annexe TEXT,
    contrat TEXT,
    typerecette TEXT,
    montantrecette DOUBLE PRECISION,
    daterecu TIMESTAMP,
    part_frais_de_fct DOUBLE PRECISION,
    enretard TEXT,
    date_de_saisie TIMESTAMP,
    code_recu TEXT,
    saisit_par TEXT
);

-- 6. Fait Sinistre
CREATE TABLE fact_sinistre (
    federation TEXT,
    ong TEXT,
    branch TEXT,
    zone TEXT,
    communaute TEXT,
    sinistre TEXT,
    produit TEXT,
    contrat TEXT,
    code_annexe TEXT,
    code_membre TEXT,
    date_de_naissance TIMESTAMP,
    sexe TEXT,
    nom TEXT,
    prenom TEXT,
    date_d_admission TIMESTAMP,
    dernier_remboursement_pour_ce_sinistre TIMESTAMP,
    reasoncharge TEXT,
    type_de_prise_en_charge TEXT,
    groupe_de_pathologie TEXT,
    probleme_diagnostique TEXT,
    categorie TEXT,
    categorie_prestataire_de_sante TEXT,
    prestataire_de_sante TEXT,
    public_prive TEXT,
    type_de_remboursement TEXT,
    montant_des_soins DOUBLE PRECISION,
    montant_rembourse DOUBLE PRECISION,
    cle_membre_contrat TEXT
);

-- 7. Fait Reçu Sinistre
CREATE TABLE fact_recu_sinistre (
    federation TEXT,
    ong TEXT,
    branch TEXT,
    zone TEXT,
    communaute TEXT,
    numero_de_piece_comptable TEXT,
    sinistre TEXT,
    recu TEXT,
    produit TEXT,
    contrat TEXT,
    code_annexe TEXT,
    code_membre TEXT,
    date_de_naissance TIMESTAMP,
    sexe TEXT,
    date_de_remboursement TIMESTAMP,
    type_de_depense TEXT,
    date_du_recu TIMESTAMP,
    nom TEXT,
    prenom TEXT,
    date_d_admission TIMESTAMP,
    type_de_prise_en_charge TEXT,
    montant_restant_a_charge DOUBLE PRECISION,
    groupe_de_pathologie TEXT,
    probleme_diagnostique TEXT,
    categorie TEXT,
    categorie_prestataire_de_sante TEXT,
    prestataire_de_sante TEXT,
    public_prive TEXT,
    montant_des_soins DOUBLE PRECISION,
    montant_rembourse DOUBLE PRECISION,
    reasoncharge TEXT,
    saisit_par TEXT,
    type_de_remboursement TEXT,
    cle_membre_contrat TEXT
);
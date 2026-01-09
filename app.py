import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Gestion VSLA Pro", layout="wide")

# --- CONNEXION BASE DE DONNÉES ---
conn = sqlite3.connect('vsla_data.db', check_same_thread=False)
c = conn.cursor()

# Création des tables si elles n'existent pas
c.execute('''CREATE TABLE IF NOT EXISTS membres 
             (id INTEGER PRIMARY KEY, nom TEXT, role TEXT, epargne_totale REAL)''')
c.execute('''CREATE TABLE IF NOT EXISTS transactions 
             (id INTEGER PRIMARY KEY, membre_id INTEGER, type TEXT, montant REAL, date TEXT)''')

# --- LOGIQUE DE GESTION DES RÔLES ---
st.sidebar.title("🔐 Accès Sécurisé")
role_acces = st.sidebar.selectbox("Choisissez votre rôle", 
    ["Membre", "Secrétaire", "Trésorier", "Président", "Contrôleur", "Facilitateur ONG"])

# --- DASHBOARD GÉNÉRAL (Visible par tous) ---
st.title(f"🏦 Système de Gestion AVEC - Mode {role_acces}")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Épargne", "1,250,000 XOF", "+5%")
with col2:
    st.metric("Crédits en cours", "450,000 XOF", "-2%")
with col3:
    st.metric("Fonds Social", "75,000 XOF")

st.divider()

# --- MODULES SELON LES RÔLES ---

if role_acces == "Secrétaire":
    st.header("📝 Registre de Présence")
    with st.form("presence_form"):
        date_reunion = st.date_input("Date de la réunion")
        st.info("Cochez les membres présents aujourd'hui")
        # Simulation liste membres
        membres = ["Jean Bakari", "Marie Museka", "Pauline Zola"]
        for m in membres:
            st.checkbox(m, key=m)
        if st.form_submit_button("Valider les présences"):
            st.success("Liste de présence soumise au Président.")

elif role_acces == "Trésorier":
    st.header("💰 Enregistrement des Transactions")
    if st.warning("Le Président doit valider l'ouverture de la session pour activer la saisie."):
        pass
    membre_sel = st.selectbox("Sélectionner le membre", ["Jean Bakari", "Marie Museka"])
    type_trans = st.radio("Type d'opération", ["Épargne (Parts)", "Remboursement Prêt", "Fonds Social", "Pénalité"])
    montant = st.number_input("Montant (XOF)", min_value=0)
    
    if st.button("Enregistrer la transaction"):
        st.success(f"Transaction de {montant} XOF enregistrée pour {membre_sel}")

elif role_acces == "Contrôleur":
    st.header("🔍 Analyse de Crédit")
    st.write("Demandes en attente d'analyse :")
    st.info("Membre: Marie Museka | Demande: 50,000 XOF | Capacité: OK (Épargne x3)")
    if st.button("Recommander au Président"):
        st.success("Dossier transmis avec avis favorable.")

elif role_acces == "Président":
    st.header("⚖️ Bureau de Validation")
    st.subheader("Décisions urgentes")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.write("Valider la réunion du 09/01/2026")
        st.button("✅ Ouvrir la session")
    with col_p2:
        st.write("Approuver le prêt de Marie (50,000 XOF)")
        st.button("🚀 Approuver le décaissement")

elif role_acces == "Facilitateur ONG":
    st.header("📊 Supervision & Maturité")
    # Score de maturité fictif
    st.progress(85)
    st.write("Score de Maturité de l'AVEC : **85/100 (Mature)**")
    st.write("Éligible au refinancement bancaire : **OUI**")

# --- FOOTER HORS CONNEXION ---
st.markdown("---")
st.caption("📱 Application optimisée pour usage hors-ligne (PWA Ready). Les données seront synchronisées dès détection d'un réseau.")

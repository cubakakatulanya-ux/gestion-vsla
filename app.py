import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.express as px

# --- CONFIGURATION INITIALE & STYLE ---
st.set_page_config(page_title="VSLA Digital Pro", layout="wide")

# --- INITIALISATION DE LA SESSION (MÉMOIRE LOCALE) ---
if 'monnaie' not in st.session_state:
    st.session_state['monnaie'] = "Non définie"
if 'reunion_ouverte' not in st.session_state:
    st.session_state['reunion_ouverte'] = False

# --- BASE DE DONNÉES (LOGIQUE SQLITE) ---
conn = sqlite3.connect('vsla_master.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS audit_trail 
             (id INTEGER PRIMARY KEY, date TEXT, utilisateur TEXT, action TEXT, details TEXT)''')

def log_audit(user, action, details):
    t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO audit_trail (date, utilisateur, action, details) VALUES (?,?,?,?)",
              (t, user, action, details))
    conn.commit()

# --- COMPOSANTS DE VALIDATION (DIALOGUES) ---
@st.dialog("Confirmation Critique")
def confirmer_action(message, callback, args=()):
    st.warning(f"⚠️ {message}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Confirmer", use_container_width=True):
            callback(*args)
            st.rerun()
    with col2:
        if st.button("❌ Annuler", use_container_width=True):
            st.rerun()

# --- LOGIQUE DE NAVIGATION (SIDEBAR) ---
st.sidebar.title("🏢 VSLA Digital v1.0")
role = st.sidebar.selectbox("Rôle de l'utilisateur", 
    ["Animateur", "Secrétaire", "Trésorier", "Contrôleur", "Président", "Membre", "Responsable ONG"])

st.sidebar.markdown(f"**Monnaie :** {st.session_state['monnaie']}")
st.sidebar.markdown(f"**Session :** {'🟢 Ouverte' if st.session_state['reunion_ouverte'] else '🔴 Close'}")

# --- 1. INTERFACE ANIMATEUR (Configuration & Agenda) ---
if role == "Animateur":
    st.title("🛠 Espace Animateur Communautaire")
    tab1, tab2 = st.tabs(["Configuration Groupe", "Agenda & Rapports"])
    
    with tab1:
        if st.session_state['monnaie'] == "Non définie":
            with st.form("config_avec"):
                nom = st.text_input("Nom de l'AVEC")
                devise = st.selectbox("Monnaie de travail", ["Franc Congolais (CDF)", "Dollar Américain (USD)"])
                val_part = st.number_input("Valeur d'une part", min_value=1)
                if st.form_submit_button("🚀 Créer le groupe"):
                    def save_config(n, d):
                        st.session_state['monnaie'] = d
                        log_audit("Animateur", "CREATION_GROUPE", f"Nom: {n}, Monnaie: {d}")
                    confirmer_action(f"Voulez-vous verrouiller la monnaie sur {devise} ?", save_config, (nom, devise))
        else:
            st.success(f"Le groupe est configuré en {st.session_state['monnaie']}")
            
    with tab2:
        st.subheader("🗓 Mon Agenda de terrain")
        st.date_input("Prochaine visite")
        st.text_area("Rapport d'activité pour l'ONG")
        if st.button("Envoyer Rapport"):
            st.toast("Rapport envoyé au responsable ONG !")

# --- 2. INTERFACE SECRÉTAIRE (Présences) ---
elif role == "Secrétaire":
    st.title("📝 Registre du Secrétariat")
    if not st.session_state['reunion_ouverte']:
        st.info("Le Président doit ouvrir la réunion pour commencer.")
    else:
        st.subheader("Pointage des présences")
        membres = ["Jean", "Marie", "Ephraim", "Zola"]
        for m in membres:
            st.checkbox(m, key=f"pres_{m}")
        if st.button("Valider la liste"):
            st.success("Liste de présence enregistrée.")

# --- 3. INTERFACE TRÉSORIER (Transactions & Confirmation) ---
elif role == "Trésorier":
    st.title(f"💰 Caisse Digitale ({st.session_state['monnaie']})")
    if not st.session_state['reunion_ouverte']:
        st.error("Action impossible : Réunion non ouverte.")
    else:
        with st.form("transac_form"):
            membre = st.selectbox("Membre", ["Jean", "Marie", "Ephraim"])
            type_op = st.selectbox("Type", ["Épargne", "Remboursement", "Fonds Social", "Pénalité"])
            montant = st.number_input("Montant", min_value=0)
            if st.form_submit_button("Enregistrer"):
                def save_tx(m, t, mo):
                    log_audit("Trésorier", t, f"Membre: {m}, Montant: {mo}")
                    st.session_state[f"last_{m}"] = mo
                confirmer_action(f"Enregistrer {type_op} de {montant} {st.session_state['monnaie']} pour {membre} ?", save_tx, (membre, type_op, montant))

# --- 4. INTERFACE PRÉSIDENT (Gouvernance & Clôture) ---
elif role == "Président":
    st.title("⚖️ Présidence du Comité")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🟢 Ouvrir la Réunion", use_container_width=True):
            st.session_state['reunion_ouverte'] = True
            log_audit("Président", "OUVERTURE_SESSION", "Session ouverte")
            st.rerun()
    with col2:
        if st.button("🔴 Clôturer la Réunion", use_container_width=True):
            st.session_state['reunion_ouverte'] = False
            log_audit("Président", "CLOTURE_SESSION", "Session fermée")
            st.rerun()

    st.divider()
    st.subheader("Partage des Dividendes (Fin de Cycle)")
    if st.button("🧮 Calculer le Partage Final"):
        st.write("Simulation du partage basée sur l'épargne cumulée...")
        st.info("Dividendes suggérés : +12% par part détenue.")

# --- 5. INTERFACE RESPONSABLE ONG (Audit & Performance) ---
elif role == "Responsable ONG":
    st.title("🏢 Pilotage stratégique ONG")
    st.subheader("Performance vs Indicateurs Projet")
    df = pd.DataFrame({'Objectif': [100, 50, 95], 'Réalisé': [85, 45, 92]}, index=['Membres', 'Épargne', 'Remboursement'])
    st.bar_chart(df)
    
    st.subheader("🕵️‍♂️ Journal d'Audit (Anti-Fraude)")
    # Extraction des logs SQL
    audit_data = c.execute("SELECT * FROM audit_trail ORDER BY id DESC LIMIT 10").fetchall()
    st.table(pd.DataFrame(audit_data, columns=['ID', 'Date', 'User', 'Action', 'Détails']))

# --- 6. INTERFACE MEMBRE & CHATBOT ---
elif role == "Membre":
    st.title("👤 Mon Espace Membre")
    st.metric("Mon Épargne", f"45,000 {st.session_state['monnaie']}")
    
    st.divider()
    st.subheader("🤖 Assistant Éducation Financière")
    question = st.text_input("Posez une question sur la gestion de votre argent :")
    if question:
        if "intérêt" in question.lower():
            st.write("L'intérêt est le loyer de l'argent. Dans notre AVEC, il aide à faire grandir la caisse pour tous.")
        else:
            st.write("L'épargne régulière est la clé de votre autonomie financière.")

# --- FOOTER ---
st.sidebar.divider()
if st.sidebar.button("📥 Exporter Rapport CSV"):
    st.sidebar.write("Téléchargement lancé...")

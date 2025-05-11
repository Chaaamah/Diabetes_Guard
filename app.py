import streamlit as st
from modules import dashboard, history, predict, patients
from auth import login_page, register_page, logout
from db import init_db

# Configuration de la page
st.set_page_config(
    page_title="Diabetes Guard",
    page_icon="🩸",
    layout="wide"
)

# Initialisation de la session
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_id" not in st.session_state:
    st.session_state["user_id"] = None
if "page" not in st.session_state:
    st.session_state["page"] = "login"

init_db()

# CSS personnalisé pour le menu latéral stylisé
st.markdown("""
<style>
.sidebar .sidebar-content {
    background-color: #1e1e2f;
    color: white;
    font-family: Arial, sans-serif;
}

.sidebar .sidebar-content h2 {
    color: #ffffff;
    font-size: 20px;
    margin-bottom: 20px;
}

.menu-button {
    background-color: #2a2a3e;
    color: white;
    border: none;
    padding: 12px 20px;
    margin: 8px 0;
    width: 100%;
    text-align: left;
    border-radius: 8px;
    font-size: 16px;
    cursor: pointer;
    transition: background-color 0.3s;
    display: flex;
    align-items: center;
}

.menu-button:hover {
    background-color: #4a4a6a;
}

.menu-button.active {
    background-color: #ff6b6b;
    font-weight: bold;
}

.menu-button i {
    margin-right: 10px;
    font-size: 18px;
}
</style>
""", unsafe_allow_html=True)

# Fonction pour changer de page
def navigate_to(page_name):
    st.session_state["page"] = page_name

# Menu latéral stylisé avec boutons
with st.sidebar:
    st.markdown("<h2>🩸 Diabetes Guard</h2>", unsafe_allow_html=True)
    
    if st.session_state["logged_in"]:
        st.button("📊 Dashboard", on_click=navigate_to, args=("Dashboard",), use_container_width=True)
        st.button("📜 Historique", on_click=navigate_to, args=("Historique",), use_container_width=True)
        st.button("🩺 Prédiction", on_click=navigate_to, args=("Prédiction",), use_container_width=True)
        st.button("👥 Patients", on_click=navigate_to, args=("Patients",), use_container_width=True)
        st.button("🚪 Déconnexion", on_click=logout, use_container_width=True)
    else:
        st.button("🔐 Connexion", on_click=navigate_to, args=("login",), use_container_width=True)
        st.button("📝 Inscription", on_click=navigate_to, args=("register",), use_container_width=True)

# Gestion des pages
if st.session_state["page"] == "login":
    login_page()
elif st.session_state["page"] == "register":
    register_page()
elif st.session_state["logged_in"]:
    if st.session_state["page"] == "Dashboard":
        dashboard.show()
    elif st.session_state["page"] == "Historique":
        history.show(st.session_state["user_id"])
    elif st.session_state["page"] == "Prédiction":
        predict.show(st.session_state["user_id"])
    elif st.session_state["page"] == "Patients":
        patients.show()
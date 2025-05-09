import streamlit as st
from db import create_user, verify_user

def login_page():
    st.title("Connexion")
    username = st.text_input("Nom d'utilisateur", key="login_username")
    password = st.text_input("Mot de passe", type="password", key="login_password")
    if st.button("Se connecter"):
        user_id = verify_user(username, password)
        if user_id:
            st.session_state["logged_in"] = True
            st.session_state["user_id"] = user_id
            st.rerun()
        else:
            st.error("Nom d'utilisateur ou mot de passe incorrect")

def register_page():
    st.title("Inscription")
    username = st.text_input("Nom d'utilisateur", key="register_username")
    password = st.text_input("Mot de passe", type="password", key="register_password")
    confirm = st.text_input("Confirmer le mot de passe", type="password", key="register_confirm")
    if st.button("S'inscrire"):
        if password != confirm:
            st.error("Les mots de passe ne correspondent pas")
            return
        success, msg = create_user(username, password)
        if success:
            st.success(msg)
            st.session_state["page"] = "login"
            st.rerun()
        else:
            st.error(msg)

def logout():
    st.session_state["logged_in"] = False
    st.session_state["user_id"] = None
    st.rerun()
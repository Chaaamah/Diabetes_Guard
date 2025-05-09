import streamlit as st
import sqlite3

def show():
    st.title("Dashboard")
    st.write("Bienvenue sur le tableau de bord")

    # Connexion à la base de données
    conn = sqlite3.connect("diabetes.db")
    cursor = conn.cursor()

    # Statistiques
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM predictions")
    pred_count = cursor.fetchone()[0]

    col1, col2 = st.columns(2)
    col1.metric("Utilisateurs", user_count)
    col2.metric("Prédictions totales", pred_count)

    # Graphique simple
    st.bar_chart({"Prédictions": [pred_count]})
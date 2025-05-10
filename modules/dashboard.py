import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import ast

def show():
    st.title("Dashboard")
    st.write("Bienvenue sur le tableau de bord")

    # Connexion à la base de données
    conn = sqlite3.connect("diabetes.db")

    # Nombre d'utilisateurs
    user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]

    # Nombre total de prédictions
    pred_count = conn.execute("SELECT COUNT(*) FROM predictions").fetchone()[0]

    # Chargement des prédictions
    df = pd.read_sql_query("SELECT * FROM predictions", conn)
    conn.close()

    # Vérification de la structure
    if df.empty or 'data' not in df.columns or 'prediction' not in df.columns:
        st.warning("Aucune donnée exploitable trouvée.")
        return

    try:
        # Conversion de la colonne 'data' en dictionnaires
        df['parsed_data'] = df['data'].apply(lambda x: ast.literal_eval(x))
        data_df = pd.json_normalize(df['parsed_data'])

        # Extraction de la classe prédite (premier caractère de 'prediction')
            # Extraction de la classe prédite (premier chiffre 0 ou 1)
        def extract_outcome(binary_str):
            for c in str(binary_str):
                if c in ['0', '1']:
                    return int(c)
            return None  # Aucun chiffre trouvé

        df['outcome'] = df['prediction'].apply(extract_outcome)
        data_df['outcome'] = df['outcome']

    except Exception as e:
        st.error(f"Erreur lors de l'analyse des données : {e}")
        return

    # Métriques principales
    col1, col2 = st.columns(2)
    col1.metric("Utilisateurs", user_count)
    col2.metric("Prédictions totales", pred_count)

    # --- 1. Graphique des prédictions ---
    st.subheader("Répartition des prédictions")
    outcome_counts = data_df["outcome"].value_counts().sort_index()
    labels = ['Non diabétique', 'Diabétique']
    values = [outcome_counts.get(0, 0), outcome_counts.get(1, 0)]

    st.bar_chart(pd.DataFrame({
        "Nombre de cas": values
    }, index=labels))

    # --- 2. Top 10 patients avec plus de glucose ---
    st.subheader("Top 10 patients avec le plus de glucose")
    if "Glucose" in data_df.columns:
        top_glucose = data_df.sort_values(by="Glucose", ascending=False).head(10)
        st.dataframe(top_glucose[["Glucose", "outcome"]])
        st.line_chart(top_glucose["Glucose"])
    else:
        st.warning("Colonne 'Glucose' manquante.")

    # --- 3. Corrélation entre variables ---
    st.subheader("Corrélation entre les variables")
    corr_cols = data_df.select_dtypes(include=np.number)
    if not corr_cols.empty:
        corr = corr_cols.corr()
        fig, ax = plt.subplots()
        sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
        st.pyplot(fig)
    else:
        st.warning("Pas de colonnes numériques pour la corrélation.")

    # --- 4. Patients urgents (Glucose > 180 et outcome == 1) ---
    st.subheader("Patients nécessitant une attention urgente")
    if "Glucose" in data_df.columns:
        urgence = data_df[(data_df["Glucose"] > 180) & (data_df["outcome"] == 1)]
        st.write(f"{len(urgence)} patients à risque élevé (glucose > 180 & diabétiques)")
        st.dataframe(urgence)
    else:
        st.warning("Colonne 'Glucose' non disponible.")


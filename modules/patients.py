import streamlit as st
import sqlite3
import pandas as pd
import ast

def show():
    st.title("Patients")

    conn = sqlite3.connect("diabetes.db")
    cursor = conn.cursor()

    query = """
    SELECT users.username, predictions.data, predictions.prediction
    FROM users
    JOIN predictions ON users.id = predictions.user_id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Parse data
    def parse_data(data_str):
        try:
            return ast.literal_eval(data_str)
        except:
            return {}

    parsed_data = df['data'].apply(parse_data)
    data_df = pd.json_normalize(parsed_data)

    data_df['username'] = df['username']
    data_df['prediction'] = df['prediction'].apply(lambda x: 'Diabétique' if '1' in x.decode('utf-8') else 'Non diabétique')


    cols = ['username'] + [col for col in data_df.columns if col not in ['username', 'prediction']] + ['prediction']
    data_df = data_df[cols]

    st.subheader("Tableau des patients avec leurs données médicales")
    st.dataframe(data_df)

    # Liste des médicaments à prescrire (fictifs)
    st.subheader("Médicaments prescrits (patients diabétiques uniquement)")

    def prescrire_medicament(glucose):
        if glucose > 200:
            return "Insuline"
        elif glucose > 140:
            return "Metformine"
        else:
            return "Régime alimentaire"

    # Ajouter la colonne médicament pour les diabétiques
    diab_df = data_df[data_df['prediction'] == 'Diabétique'].copy()
    diab_df['Médicament'] = diab_df['Glucose'].apply(prescrire_medicament)

    # Affichage sous forme de tableau
    st.dataframe(diab_df[['username', 'Glucose', 'Médicament']])

    # Graphique des prescriptions
    med_counts = diab_df['Médicament'].value_counts()
    st.bar_chart(med_counts)

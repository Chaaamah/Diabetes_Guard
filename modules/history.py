import streamlit as st
from db import get_predictions
import pandas as pd
import altair as alt

def show(user_id):
    st.title("Historique des prédictions")
    
    # Récupérer les prédictions de l'utilisateur
    preds = get_predictions(user_id)
    if not preds:
        st.info("Aucune prédiction enregistrée")
        return
    
    # Convertir les données en DataFrame
    df = pd.DataFrame(preds, columns=["data", "prediction"])
    df["date"] = pd.to_datetime("now")  # Remplacer par la date réelle si disponible
    df["risque"] = df["prediction"].apply(lambda x: "Risque élevé" if x == 1 else "Risque faible")
    
    # Visualisation 1 : Répartition des risques
    st.subheader("Répartition des risques")
    
    # Utiliser value_counts() avec des noms de colonnes explicites
    risk_counts = df["risque"].value_counts().reset_index()
    risk_counts.columns = ["categorie", "count"]  # Renommer les colonnes

    # Créer le graphique avec des noms de colonnes clairs
    fig = alt.Chart(risk_counts).mark_bar().encode(
        x=alt.X("categorie:N", title="Catégorie"),  # ":N" indique que c'est nominal
        y=alt.Y("count:Q", title="Nombre de prédictions"),
        color=alt.Color("categorie:N", scale=alt.Scale(domain=["Risque faible", "Risque élevé"], range=["green", "red"]))
    ).properties(width=600)
    st.altair_chart(fig, use_container_width=True)
    
    # Visualisation 2 : Timeline des prédictions
    st.subheader("Timeline des prédictions")
    timeline = alt.Chart(df).mark_circle(size=100).encode(
        x='date:T',
        y=alt.Y('risque:N', sort=['Risque faible', 'Risque élevé']),
        color=alt.Color('risque:N', scale=alt.Scale(domain=["Risque faible", "Risque élevé"], range=["green", "red"])),
        tooltip=['date:T', 'risque:N']
    ).properties(width=800)
    st.altair_chart(timeline)
    
    # Visualisation 3 : Détails des dernières prédictions
    st.subheader("Détails des dernières prédictions")
    latest_preds = df.head(5)
    st.table(latest_preds[["date", "risque", "data"]])
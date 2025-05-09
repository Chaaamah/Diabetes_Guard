import streamlit as st
import pandas as pd
import joblib
import os
from db import save_prediction
from fpdf import FPDF

# Charger le modèle et le scaler
model = joblib.load("models/diabetes_model.pkl")
scaler = joblib.load("models/scaler.pkl")

def generate_pdf_report(data, prediction):
    report_dir = "reports"
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
    filename = os.path.join(report_dir, "rapport_diabete.pdf")
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    # Titre
    pdf.cell(200, 10, txt="Rapport de prédiction du risque de diabète", ln=True, align="C")

    # Résultat
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Résultat : {'Risque élevé' if prediction == 1 else 'Risque faible'}", ln=True)

    # Détails des données
    pdf.ln(10)
    pdf.cell(200, 10, txt="Détails des données saisies :", ln=True)
    for key, value in data.items():
        pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)

    pdf.output(filename)
    return filename

def validate_input(data):
    for key, value in data.items():
        if value < 0:
            raise ValueError(f"Valeur négative non valide pour '{key}'")
    return True

def show(user_id):
    st.title("Prédiction du risque de diabète")
    st.write("Veuillez renseigner vos données médicales :")

    pregnancies = st.number_input("Nombre de grossesses", min_value=0, step=1, key="predict_pregnancies")
    glucose = st.number_input("Niveau de glucose (mg/dL)", min_value=0, key="predict_glucose")
    blood_pressure = st.number_input("Pression artérielle (mm Hg)", min_value=0, key="predict_blood_pressure")
    skin_thickness = st.number_input("Épaisseur cutanée (mm)", min_value=0, key="predict_skin_thickness")
    insulin = st.number_input("Insuline (μU/mL)", min_value=0, key="predict_insulin")
    bmi = st.number_input("Indice de masse corporelle (BMI)", min_value=0.0, key="predict_bmi")
    pedigree = st.number_input("Fonction de pedigree du diabète", min_value=0.0, key="predict_pedigree")
    age = st.number_input("Âge (années)", min_value=0, step=1, key="predict_age")

    if st.button("Prédire"):
        try:
            
            # Créer la feature manquante (insulin_glucose_ratio)
            insulin_glucose_ratio = insulin / glucose if glucose != 0 else 0

            # Créer le dictionnaire avec toutes les features attendues
            data = {
                "Pregnancies": int(pregnancies),
                "Glucose": float(glucose),
                "BloodPressure": float(blood_pressure),
                "SkinThickness": float(skin_thickness),
                "Insulin": float(insulin),
                "BMI": float(bmi),
                "DiabetesPedigreeFunction": float(pedigree),
                "Age": int(age),
                "insulin_glucose_ratio": float(insulin_glucose_ratio)
            }

            # Valider les données
            validate_input(data)

            # Convertir en DataFrame
            input_df = pd.DataFrame([data])

            # Normaliser les données
            input_scaled = scaler.transform(input_df)

            # Prédiction
            prediction = model.predict(input_scaled)[0]

            # Afficher le résultat
            if prediction == 1:
                st.error("Risque élevé de diabète")
            else:
                st.success("Risque faible de diabète")

            # Enregistrez la prédiction dans la base de données
            save_prediction(user_id, data, prediction)

            # Générer le rapport PDF
            filename = generate_pdf_report(data, prediction)
            with open(filename, "rb") as f:
                st.download_button("Télécharger le rapport PDF", f, file_name="rapport_diabete.pdf")

        except ValueError as e:
            st.error(f"Erreur dans les données saisies : {e}")
        except Exception as e:
            st.error(f"Une erreur s'est produite : {e}")
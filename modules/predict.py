import streamlit as st
import pandas as pd
import joblib
import os
import sqlite3
from db import save_prediction, get_db
from fpdf import FPDF
from datetime import datetime

# Configuration des chemins
FONT_DIR = "fonts"
DEJAVU_SANS = os.path.join(FONT_DIR, "DejaVuSansCondensed.ttf")
DEJAVU_SANS_BOLD = os.path.join(FONT_DIR, "DejaVuSansCondensed-Bold.ttf")
DEJAVU_SANS_ITALIC = os.path.join(FONT_DIR, "DejaVuSansCondensed-Oblique.ttf")

# Charger le modèle et le scaler
model = joblib.load("models/diabetes_model.pkl")
scaler = joblib.load("models/scaler.pkl")

def setup_pdf_fonts(pdf):
    """Configure les polices Unicode pour le PDF"""
    try:
        pdf.add_font('DejaVu', '', DEJAVU_SANS, uni=True)
        pdf.add_font('DejaVu', 'B', DEJAVU_SANS_BOLD, uni=True)
        pdf.add_font('DejaVu', 'I', DEJAVU_SANS_ITALIC, uni=True)
    except:
        pdf.add_font('Arial', '', 'arial.ttf')
        pdf.add_font('Arial', 'B', 'arialbd.ttf')
        pdf.add_font('Arial', 'I', 'ariali.ttf')

def generate_pdf_report(patient_name, data, prediction):
    """Génère un rapport PDF avec les résultats"""
    report_dir = "reports"
    os.makedirs(report_dir, exist_ok=True)
    filename = os.path.join(report_dir, f"rapport_diabete_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    
    pdf = FPDF()
    pdf.add_page()
    setup_pdf_fonts(pdf)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(left=15, top=15, right=15)
    
    # Logo
    try:
        pdf.image("assets/logo.jpg", x=15, y=10, w=25)
    except:
        pass
    
    # Titre
    pdf.set_font('DejaVu', 'B', 16)
    pdf.ln(20)
    pdf.cell(0, 10, "Cabinet Médical Diabetes Guard", ln=True, align='C')
    pdf.set_font('DejaVu', 'B', 14)
    pdf.cell(0, 10, "Rapport d'analyse du risque diabétique", ln=True, align='C')
    
    # Informations patient
    pdf.set_font('DejaVu', 'B', 12)
    pdf.cell(40, 8, "Patient: ", ln=0)
    pdf.set_font('DejaVu', '', 12)
    pdf.cell(0, 8, patient_name, ln=True)
    
    pdf.set_font('DejaVu', 'B', 12)
    pdf.cell(40, 8, "Date: ", ln=0)
    pdf.set_font('DejaVu', '', 12)
    pdf.cell(0, 8, datetime.now().strftime("%d/%m/%Y %H:%M"), ln=True)
    pdf.ln(10)
    
    # Résultat
    pdf.set_font('DejaVu', 'B', 14)
    result = "RISQUE ÉLEVÉ DE DIABÈTE" if prediction == 1 else "RISQUE FAIBLE DE DIABÈTE"
    pdf.set_text_color(255, 0, 0) if prediction == 1 else pdf.set_text_color(0, 128, 0)
    pdf.cell(0, 10, result, ln=True, align='C')
    pdf.set_text_color(0, 0, 0)
    pdf.ln(10)
    
    # Tableau des paramètres
    col_widths = [80, 40, 40]
    pdf.set_font('DejaVu', 'B', 12)
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(col_widths[0], 8, "Paramètre", border=1, fill=True)
    pdf.cell(col_widths[1], 8, "Valeur", border=1, fill=True)
    pdf.cell(col_widths[2], 8, "Norme", border=1, fill=True, ln=True)
    
    pdf.set_font('DejaVu', '', 10)
    params = [
        ("Glucose (mg/dL)", data["Glucose"], "70-140"),
        ("Pression artérielle (mm Hg)", data["BloodPressure"], "<120/80"),
        ("Indice de masse corporelle", data["BMI"], "18.5-25"),
        ("Âge (années)", data["Age"], ""),
        ("Grossesses", data["Pregnancies"], ""),
        ("Insuline (microU/mL)", data["Insulin"], "2-25"),
        ("Fonction pedigree", data["DiabetesPedigreeFunction"], ""),
    ]
    
    for param in params:
        pdf.cell(col_widths[0], 8, param[0], border=1)
        pdf.cell(col_widths[1], 8, str(param[1]), border=1)
        pdf.cell(col_widths[2], 8, param[2], border=1, ln=True)
    
    pdf.ln(10)
    
    # Recommandations
    pdf.set_font('DejaVu', 'B', 12)
    pdf.cell(0, 8, "Recommandations médicales:", ln=True)
    pdf.set_font('DejaVu', '', 11)
    
    advice = [
        "1. Consultation endocrinologique recommandée",
        "2. Contrôle glycémique régulier (3 fois/semaine)",
        "3. Régime pauvre en sucres rapides",
        "4. Activité physique 30 min/jour",
        "5. Éviter alcool et tabac",
        "6. Bilan sanguin sous 15 jours"
    ] if prediction == 1 else [
        "1. Alimentation équilibrée",
        "2. Activité physique régulière",
        "3. Contrôle annuel de glycémie",
        "4. Surveillance IMC",
        "5. Limiter sucres rapides",
        "6. Consultation prévention 2 ans"
    ]
    
    for item in advice:
        pdf.multi_cell(0, 7, item)
        pdf.ln(2)
    
    # Signature
    pdf.ln(15)
    pdf.set_font('DejaVu', 'I', 12)
    pdf.cell(0, 8, "Le médecin traitant,", ln=True)
    pdf.ln(10)
    pdf.cell(0, 8, "Dr. Jean Dupont", ln=True)
    pdf.cell(0, 6, "Diplômé en endocrinologie", ln=True)
    pdf.cell(0, 6, "Cabinet Diabetes Guard", ln=True)
    
    pdf.output(filename)
    return filename

def validate_input(data):
    for key, value in data.items():
        if value < 0:
            raise ValueError(f"Valeur négative non valide pour '{key}'")
    return True

def show(user_id):
    st.title("Prédiction du risque de diabète")
    
    # Récupérer la liste des patients
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nom, prenom FROM patients ORDER BY nom, prenom")
        patients = cursor.fetchall()
        conn.close()
        
        if not patients:
            st.warning("Aucun patient enregistré. Veuillez d'abord créer un patient.")
            return
            
        patients_options = [f"{p[1]} {p[2]}" for p in patients]
        selected_patient = st.selectbox("Sélectionner un patient", patients_options)
        patient_id = [p[0] for p in patients if f"{p[1]} {p[2]}" == selected_patient][0]
        
        # Initialisation de l'état de session pour stocker les résultats
        if 'prediction_results' not in st.session_state:
            st.session_state.prediction_results = None
    
        # Formulaire de saisie
        with st.form("medical_form"):
            st.write(f"Veuillez renseigner les données médicales pour {selected_patient}:")
            
            col1, col2 = st.columns(2)
            with col1:
                pregnancies = st.number_input("Nombre de grossesses", min_value=0, step=1)
                glucose = st.number_input("Niveau de glucose (mg/dL)", min_value=0)
                blood_pressure = st.number_input("Pression artérielle (mm Hg)", min_value=0)
                skin_thickness = st.number_input("Épaisseur cutanée (mm)", min_value=0)
            with col2:
                insulin = st.number_input("Insuline (microU/mL)", min_value=0)
                bmi = st.number_input("Indice de masse corporelle (BMI)", min_value=0.0)
                pedigree = st.number_input("Fonction de pedigree du diabète", min_value=0.0)
                age = st.number_input("Âge (années)", min_value=0, step=1)
            
            submitted = st.form_submit_button("Prédire")
            
            if submitted:
                try:
                    # Préparation des données
                    insulin_glucose_ratio = insulin / glucose if glucose != 0 else 0
                    data = {
                        "Pregnancies": pregnancies,
                        "Glucose": glucose,
                        "BloodPressure": blood_pressure,
                        "SkinThickness": skin_thickness,
                        "Insulin": insulin,
                        "BMI": bmi,
                        "DiabetesPedigreeFunction": pedigree,
                        "Age": age,
                        "insulin_glucose_ratio": insulin_glucose_ratio
                    }
                    
                    validate_input(data)
                    
                    # Prédiction
                    input_df = pd.DataFrame([data])
                    input_scaled = scaler.transform(input_df)
                    prediction = model.predict(input_scaled)[0]
                    
                    # Sauvegarde des résultats dans la session
                    st.session_state.prediction_results = {
                        'patient_name': selected_patient,
                        'data': data,
                        'prediction': prediction,
                        'pdf_path': generate_pdf_report(selected_patient, data, prediction)
                    }
                    
                    # Affichage des résultats
                    if prediction == 1:
                        st.error(f"Risque élevé de diabète pour {selected_patient}")
                    else:
                        st.success(f"Risque faible de diabète pour {selected_patient}")
                    
                    # Sauvegarde en base de données
                    save_prediction(user_id, data, prediction)
                    
                except ValueError as e:
                    st.error(f"Erreur dans les données saisies : {e}")
                except Exception as e:
                    st.error(f"Une erreur s'est produite : {e}")
    
        # Bouton de téléchargement (en dehors du formulaire)
        if st.session_state.prediction_results:
            with open(st.session_state.prediction_results['pdf_path'], "rb") as f:
                st.download_button(
                    "Télécharger le rapport PDF",
                    data=f,
                    file_name=f"rapport_diabete_{st.session_state.prediction_results['patient_name'].replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
                    
    except sqlite3.Error as e:
        st.error(f"Erreur de base de données: {e}")
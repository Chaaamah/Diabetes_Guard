import streamlit as st
import sqlite3
import pandas as pd
import ast
from datetime import datetime

def init_db_connection():
    return sqlite3.connect("diabetes.db")

def cancel_action():
    st.session_state.current_tab = "📋 Liste"
    st.session_state.selected_patient_id = None
    st.session_state.confirm_delete = False

def show():
    conn = init_db_connection()

    st.markdown("""<style>
    .action-button {font-size: 12px; padding: 5px 8px; margin: 2px;}
    </style>""", unsafe_allow_html=True)

    st.title("👥 Gestion des Patients")

    with conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            age INTEGER,
            sexe TEXT,
            telephone TEXT,
            email TEXT,
            date_creation TEXT,
            notes TEXT
        )
        """)

    if "current_tab" not in st.session_state:
        st.session_state.current_tab = "📋 Liste"

    disabled = st.session_state.current_tab != "📋 Liste"

    if st.session_state.current_tab == "📋 Liste":
        display_patients_table(conn, disabled)
        st.markdown("---")
        display_medical_data(conn, disabled)

    elif st.session_state.current_tab == "➕ Ajouter":
        add_patient_form(conn)

    elif st.session_state.current_tab == "✏️ Modifier":
        update_patient_form(conn)

    elif st.session_state.current_tab == "🗑️ Supprimer":
        delete_patient_form(conn)

    conn.close()

def display_patients_table(conn, disabled):
    st.subheader("Liste complète des patients")

    df = pd.read_sql_query("SELECT * FROM patients ORDER BY nom, prenom", conn)
    if df.empty:
        st.info("Aucun patient enregistré.")
        return

    if st.button("➕ Ajouter un nouveau patient", use_container_width=True, disabled=disabled):
        st.session_state.current_tab = "➕ Ajouter"

    st.write("### 📋 Tableau des patients")

    for index, row in df.iterrows():
        cols = st.columns([4, 4, 1, 1])
        cols[0].write(f"{row['nom']} {row['prenom']}")
        cols[1].write(f"{row['age']} ans - {row['sexe']}")
        cols[2].button("✏️", key=f"edit_{row['id']}",
                       on_click=lambda pid=row['id']: set_edit_delete(pid, "✏️ Modifier"),
                       disabled=disabled)
        cols[3].button("🗑️", key=f"delete_{row['id']}",
                       on_click=lambda pid=row['id']: set_edit_delete(pid, "🗑️ Supprimer"),
                       disabled=disabled)

def set_edit_delete(patient_id, tab):
    st.session_state.selected_patient_id = patient_id
    st.session_state.current_tab = tab

def add_patient_form(conn):
    st.subheader("Formulaire d'ajout de patient")
    with st.form("add_patient_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nom = st.text_input("Nom*", max_chars=50)
        with col2:
            prenom = st.text_input("Prénom*", max_chars=50)
        col3, col4 = st.columns(2)
        with col3:
            age = st.number_input("Âge", min_value=0, max_value=120, value=30)
        with col4:
            sexe = st.selectbox("Sexe", ["", "Masculin", "Féminin", "Autre"])
        telephone = st.text_input("Téléphone", max_chars=20)
        email = st.text_input("Email", max_chars=100)
        notes = st.text_area("Notes médicales")

        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("💾 Enregistrer")
        with col2:
            cancel = st.form_submit_button("❌ Annuler")

        if submitted:
            if not nom or not prenom:
                st.error("Nom et prénom obligatoires.")
            else:
                try:
                    conn.execute("""
                    INSERT INTO patients (nom, prenom, age, sexe, telephone, email, date_creation, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                                 (nom, prenom, age, sexe, telephone, email, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), notes))
                    conn.commit()
                    st.success(f"✅ Patient {prenom} {nom} ajouté.")
                    cancel_action()
                except Exception as e:
                    st.error(f"❌ Erreur: {e}")

        if cancel:
            cancel_action()

def update_patient_form(conn):
    st.subheader("Modifier un patient")
    if "selected_patient_id" not in st.session_state:
        st.warning("Sélectionnez un patient.")
        return

    patient_id = st.session_state.selected_patient_id
    data = conn.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()
    if not data:
        st.error("Patient introuvable.")
        return

    with st.form("update_patient_form"):
        col1, col2 = st.columns(2)
        with col1:
            nom = st.text_input("Nom*", value=data[1])
        with col2:
            prenom = st.text_input("Prénom*", value=data[2])
        col3, col4 = st.columns(2)
        with col3:
            age = st.number_input("Âge", 0, 120, data[3])
        with col4:
            sexe = st.selectbox("Sexe", ["", "Masculin", "Féminin", "Autre"],
                                index=["", "Masculin", "Féminin", "Autre"].index(data[4] or ""))
        telephone = st.text_input("Téléphone", value=data[5])
        email = st.text_input("Email", value=data[6])
        notes = st.text_area("Notes médicales", value=data[8])

        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("💾 Mettre à jour")
        with col2:
            cancel = st.form_submit_button("❌ Annuler")

        if submitted:
            if not nom or not prenom:
                st.error("Nom et prénom obligatoires.")
            else:
                try:
                    conn.execute("""
                    UPDATE patients SET nom=?, prenom=?, age=?, sexe=?, telephone=?, email=?, notes=? WHERE id=?""",
                                 (nom, prenom, age, sexe, telephone, email, notes, patient_id))
                    conn.commit()
                    st.success("✅ Patient mis à jour.")
                    cancel_action()
                except Exception as e:
                    st.error(f"❌ Erreur: {e}")

        if cancel:
            cancel_action()

def delete_patient_form(conn):
    st.subheader("Supprimer un patient")
    if "selected_patient_id" not in st.session_state:
        st.warning("Sélectionnez un patient.")
        return

    patient_id = st.session_state.selected_patient_id
    data = conn.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()
    if not data:
        st.error("Patient introuvable.")
        return

    st.warning(f"⚠️ Suppression de : {data[2]} {data[1]}")
    st.write(f"Âge : {data[3]} ans, Email : {data[6]}")
    st.write(f"Notes : {data[8] or 'Aucune note.'}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Confirmer la suppression"):
            try:
                conn.execute("DELETE FROM patients WHERE id=?", (patient_id,))
                conn.commit()
                st.success("✅ Patient supprimé.")
                cancel_action()
            except Exception as e:
                st.error(f"❌ Erreur : {e}")
    with col2:
        if st.button("❌ Annuler"):
            cancel_action()

def display_medical_data(conn, disabled):
    if disabled:
        st.info("⚙️ Opération en cours — données désactivées.")
        return

    st.subheader("📊 Données médicales et prescriptions")
    query = """
    SELECT patients.nom, patients.prenom, predictions.data, predictions.prediction
    FROM patients
    JOIN predictions ON patients.nom || ' ' || patients.prenom = predictions.username
    """
    df = pd.read_sql_query(query, conn)

    def parse_data(data_str):
        try:
            return ast.literal_eval(data_str)
        except:
            return {}

    if not df.empty:
        parsed_data = df['data'].apply(parse_data)
        data_df = pd.json_normalize(parsed_data)
        data_df['nom'] = df['nom']
        data_df['prenom'] = df['prenom']

        def convert_prediction(pred):
            if isinstance(pred, bytes):
                return int.from_bytes(pred, byteorder='little')
            try:
                return int(pred)
            except:
                return 0

        data_df['prediction'] = df['prediction'].apply(convert_prediction)
        data_df['risque'] = data_df['prediction'].apply(lambda x: 'Diabétique' if x == 1 else 'Non diabétique')

        st.dataframe(
            data_df[['nom','prenom', 'risque', 'Glucose', 'BMI', 'Age', 'BloodPressure']],
            hide_index=True
        )

        diab_df = data_df[data_df['risque'] == 'Diabétique']
        if not diab_df.empty:
            st.subheader("💊 Prescriptions pour patients diabétiques")

            def get_prescription(glucose):
                if glucose > 200: return "Insuline"
                elif glucose > 140: return "Metformine"
                else: return "Régime alimentaire"

            diab_df['Prescription'] = diab_df['Glucose'].apply(get_prescription)
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Patients nécessitant un traitement:**")
                st.dataframe(diab_df[['username', 'Glucose', 'Prescription']], hide_index=True)
            with col2:
                st.write("**Répartition des prescriptions :**")
                pres_counts = diab_df['Prescription'].value_counts()
                st.bar_chart(pres_counts)
        else:
            st.info("ℹ️ Aucun patient diabétique dans les données actuelles")
    else:
        st.info("ℹ️ Aucune donnée médicale disponible")

if __name__ == "__main__":
    show()

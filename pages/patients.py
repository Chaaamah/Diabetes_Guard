import streamlit as st
import sqlite3

def show():
    st.title("Patients")
    conn = sqlite3.connect("diabetes.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users")
    users = cursor.fetchall()
    conn.close()
    
    st.table(users)
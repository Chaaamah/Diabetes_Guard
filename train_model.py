import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib

# Charger les données
df = pd.read_csv("data/diabetes.csv")

# Feature Engineering : Calculer insulin_glucose_ratio en évitant la division par zéro
df["insulin_glucose_ratio"] = np.where(
    df["Glucose"] == 0,
    0,  # Remplacer par 0 si Glucose = 0
    df["Insulin"] / df["Glucose"]
)

# Remplacer les NaN (au cas où)
df["insulin_glucose_ratio"] = df["insulin_glucose_ratio"].fillna(0)

# Préparer les données
X = df.drop("Outcome", axis=1)
y = df["Outcome"]

# Vérifier les valeurs infinies
if np.isinf(X).any().any():
    st.error("Des valeurs infinies ont été détectées dans les données.")
    X = X.replace([np.inf, -np.inf], 0)  # Remplacer les infinis par 0

# Normalisation
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Entraîner le modèle
model = RandomForestClassifier(n_estimators=100)
model.fit(X_scaled, y)

# Sauvegarder le modèle et le scaler
joblib.dump(model, "models/diabetes_model.pkl")
joblib.dump(scaler, "models/scaler.pkl")

print("Modèle et scaler sauvegardés !")

import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier

st.set_page_config(page_title="Sb Mafia - Prédiction Foot IA", layout="centered")

st.title("⚽ Sb Mafia - Prédictions IA sur les matchs de foot")

st.markdown("""
Bienvenue sur **Sb Mafia**, l'outil intelligent qui analyse les matchs de football 
et te donne des **prédictions IA** sur le résultat (1/N/2).  
Charge un fichier CSV contenant les matchs passés avec forme des équipes.
""")

uploaded_file = st.file_uploader("📂 Upload ton fichier CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    if 'HForm' not in df.columns or 'AForm' not in df.columns or 'FTR' not in df.columns:
        st.error("❌ Le fichier doit contenir les colonnes : 'HForm', 'AForm', 'FTR'")
    else:
        st.success("✅ Fichier chargé avec succès !")

        st.subheader("Aperçu des données")
        st.dataframe(df.head())

        X = df[['HForm', 'AForm']]
        y = df['FTR']

        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)

        st.subheader("💡 Prédiction IA")
        hform = st.slider("Forme de l'équipe à domicile (HForm)", 0, 5, 3)
        aform = st.slider("Forme de l'équipe à l'extérieur (AForm)", 0, 5, 2)

        prediction = model.predict([[hform, aform]])[0]
        probas = model.predict_proba([[hform, aform]])[0]

        st.write(f"### 📊 Résultat prédit : **{prediction}**")
        st.write("Probabilités :")
        for label, prob in zip(model.classes_, probas):
            st.write(f"- {label} : {prob*100:.1f}%")
else:
    st.info("💡 Charge un fichier CSV pour commencer.")

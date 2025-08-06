import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

st.title("⚽️ Sb Mafia – Prédictions IA sur les matchs du jour")

# Chargement du CSV
try:
    df = pd.read_csv("matches_today_form.csv")

    # Vérification des colonnes nécessaires
    if all(col in df.columns for col in ["HForm", "AForm", "FTR"]):
        # Convertir les formes (W/D/L) en score moyen
        def convert_form(form):
            scores = {'W': 3, 'D': 1, 'L': 0}
            return sum([scores.get(c, 0) for c in str(form)]) / len(form)

        df["HFormScore"] = df["HForm"].apply(convert_form)
        df["AFormScore"] = df["AForm"].apply(convert_form)

        # Supprimer les lignes avec FTR manquant (si match pas encore joué)
        df_model = df.dropna(subset=["FTR"])

        if not df_model.empty:
            # Entraînement du modèle IA
            X = df_model[["HFormScore", "AFormScore"]]
            y = df_model["FTR"]

            model = RandomForestClassifier()
            model.fit(X, y)

            # Prédictions sur tous les matchs
            df["Prediction"] = model.predict(df[["HFormScore", "AFormScore"]])

            # Affichage
            st.success("✅ Prédictions générées avec succès !")
            st.dataframe(df[["HomeTeam", "AwayTeam", "HForm", "AForm", "FTR", "HFormScore", "AFormScore", "Prediction"]])
        else:
            st.warning("⚠️ Aucune donnée historique avec 'FTR' pour entraîner le modèle.")
    else:
        st.error("❌ Le fichier CSV ne contient pas les colonnes : HForm, AForm, FTR")
except FileNotFoundError:
    st.error("❌ Le fichier 'matches_today_form.csv' est introuvable.")
except Exception as e:
    st.error(f"❌ Erreur inattendue : {e}")

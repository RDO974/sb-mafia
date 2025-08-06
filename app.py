import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

st.title("⚽ Sb Mafia – Prédictions IA + Confiance + Value Bet")

# Chargement des données
try:
    df = pd.read_csv("matches_today_form.csv")

    if all(col in df.columns for col in ["HForm", "AForm", "FTR"]):
        # Convertir la forme en score numérique
        def form_to_score(form):
            form = str(form)
            scores = {'W': 3, 'D': 1, 'L': 0}
            return sum([scores.get(c, 0) for c in form if c in scores]) / len(form)

        df["HFormScore"] = df["HForm"].apply(form_to_score)
        df["AFormScore"] = df["AForm"].apply(form_to_score)

        # Sélection des données d'entraînement
        train_df = df.dropna(subset=["FTR"])
        X_train = train_df[["HFormScore", "AFormScore"]]
        y_train = train_df["FTR"]

        # Modèle IA
        model = RandomForestClassifier()
        model.fit(X_train, y_train)

        # Prédictions et probabilités
        X_pred = df[["HFormScore", "AFormScore"]]
        df["Prediction"] = model.predict(X_pred)
        proba = model.predict_proba(X_pred)

        # Ajouter les probabilités max (confiance)
        df["Confidence"] = proba.max(axis=1).round(2)

        st.success("✅ Prédictions générées avec taux de confiance.")
        st.dataframe(df[["HomeTeam", "AwayTeam", "HForm", "AForm", "Prediction", "Confidence"]])

        # Bouton Value Bet
        if st.button("💡 Afficher les Value Bets recommandés"):
            value_bets = df[df["Confidence"] >= 0.70]
            if not value_bets.empty:
                st.subheader("📈 Value Bets (confiance ≥ 70%)")
                st.dataframe(value_bets[["HomeTeam", "AwayTeam", "Prediction", "Confidence"]])
            else:
                st.info("Aucun Value Bet trouvé aujourd'hui.")
    else:
        st.error("❌ Le fichier CSV ne contient pas les colonnes : HForm, AForm, FTR")
except FileNotFoundError:
    st.error("❌ Fichier 'matches_today_form.csv' introuvable.")
except Exception as e:
    st.error(f"❌ Erreur : {e}")

import streamlit as st
import pandas as pd

# Titre de l'application
st.title("🧠 Prédictions des matchs avec formes des équipes")

# Chargement du fichier CSV
try:
    df = pd.read_csv("matches_today_form.csv")  # Remplace si tu utilises un autre nom

    # Fonction de conversion W/D/L en score moyen
    def convert_form_to_score(form_str):
        scores = {'W': 3, 'D': 1, 'L': 0}
        return sum([scores.get(c, 0) for c in form_str]) / len(form_str)

    # Appliquer la conversion
    df["HFormScore"] = df["HForm"].apply(convert_form_to_score)
    df["AFormScore"] = df["AForm"].apply(convert_form_to_score)

    # Afficher le tableau
    st.subheader("📊 Table des matchs et formes converties")
    st.dataframe(df)

except FileNotFoundError:
    st.error("❌ Le fichier 'matches_today_form.csv' est introuvable dans le dossier du projet.")
except Exception as e:
    st.error(f"❌ Une erreur s'est produite : {e}")

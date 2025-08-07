import streamlit as st
import pandas as pd
import fetch_matches

# Génère automatiquement le fichier CSV
fetch_matches.generate_csv()

# Puis charge le fichier
df = pd.read_csv("matches_today_form.csv")

st.set_page_config(page_title="Sb Mafia - IA Football", layout="wide")

st.title("⚽ Sb Mafia - Prédictions de matchs avec IA")

st.markdown("### 📅 Matchs du jour")

# Générer le fichier CSV automatiquement
with st.spinner("Chargement des matchs en cours..."):
    fetch_matches.generate_csv()

try:
    df = pd.read_csv("matches_today_form.csv")
    st.success("✅ Fichier chargé avec succès")
    st.dataframe(df)

    st.markdown("### 📈 Analyse simplifiée")

    if "HForm" in df.columns and "AForm" in df.columns:
        df["HPoints"] = df["HForm"].apply(lambda x: sum([3 if c == "W" else 1 if c == "D" else 0 for c in x]))
        df["APoints"] = df["AForm"].apply(lambda x: sum([3 if c == "W" else 1 if c == "D" else 0 for c in x]))
        df["Prediction"] = df.apply(lambda row: "Victoire Domicile" if row["HPoints"] > row["APoints"]
                                    else "Victoire Extérieur" if row["HPoints"] < row["APoints"] else "Match Nul", axis=1)
        st.dataframe(df[["HomeTeam", "AwayTeam", "HForm", "AForm", "Prediction"]])
    else:
        st.warning("Les colonnes de forme ne sont pas disponibles.")

except FileNotFoundError:
    st.error("Fichier 'matches_today_form.csv' introuvable.")
except Exception as e:
    st.exception(e)

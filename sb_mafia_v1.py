# sb_mafia_v1.py
import os, time, math, requests
import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

# ========== CONFIG ==========
THEODDS_API_KEY = os.getenv("7b5060f451264cd38ba57cfb13420e17", "7b5060f451264cd38ba57cfb13420e17")
FOOTBALL_DATA_API_KEY = os.getenv("7b5060f451264cd38ba57cfb13420e17", "7b5060f451264cd38ba57cfb13420e17")  # optional
TELEGRAM_BOT_TOKEN = os.getenv("8213824799:AAE0SOnuNgNWwDCE4v1Kt", "")
TELEGRAM_CHAT_ID = os.getenv("https://t.me/erdoganlevrai", "")

SPORT = "soccer_epl"   # exemple : soccer_epl ; tu pourras changer dans l'UI
REGIONS = "eu"         # eu, us, au, etc.
MARKETS = "h2h"        # home/draw/away market key
VALUE_THRESHOLD = 0.05 # ex: prob_model - prob_implied > 0.05

# ========== HELPERS ==========
def fetch_odds(sport_key=SPORT, regions=REGIONS, markets=MARKETS):
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds"
    params = {"regions": regions, "markets": markets, "oddsFormat": "decimal", "apiKey": THEODDS_API_KEY}
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    return r.json()

def implied_prob_from_decimal(o):
    # simple implied probability
    return 1.0 / o if o and o > 0 else 0.0

def normalize_implied_prob(probs):
    s = sum(probs)
    if s == 0: 
        return probs
    return [p/s for p in probs]

def estimate_poisson_probs(home_goals_avg, away_goals_avg, max_goals=7):
    # Build distribution for home and away and compute P(home>away)
    home_pmf = [poisson.pmf(i, home_goals_avg) for i in range(0, max_goals+1)]
    away_pmf = [poisson.pmf(j, away_goals_avg) for j in range(0, max_goals+1)]
    p_home_win = 0.0
    p_draw = 0.0
    p_away_win = 0.0
    for i in range(len(home_pmf)):
        for j in range(len(away_pmf)):
            prob = home_pmf[i] * away_pmf[j]
            if i > j:
                p_home_win += prob
            elif i == j:
                p_draw += prob
            else:
                p_away_win += prob
    # ensure numeric stability
    tot = p_home_win + p_draw + p_away_win
    return [p_home_win/tot, p_draw/tot, p_away_win/tot]

def estimate_expected_goals(team_recent, opp_recent):
    # team_recent, opp_recent : dicts with 'for_avg' and 'against_avg' per match
    # A very simple heuristic: lambda_home = (team_for_avg + opp_against_avg) / 2
    home_lambda = (team_recent.get("for_avg",1.2) + opp_recent.get("against_avg",1.2)) / 2
    away_lambda = (opp_recent.get("for_avg",1.0) + team_recent.get("against_avg",1.0)) / 2
    return max(0.05, home_lambda), max(0.05, away_lambda)

# ========== STREAMLIT UI ==========
st.title("Sb Mafia — V1 (Value bets scanner)")

col1, col2 = st.columns([3,1])
with col1:
    sport_choice = st.text_input("Sport key (TheOddsAPI)", SPORT)
    region_choice = st.text_input("Regions (eu/us/au)", REGIONS)
    market_choice = st.text_input("Market (ex: h2h)", MARKETS)
    threshold = st.number_input("Seuil value (prob_model - prob_implied)", VALUE_THRESHOLD, step=0.01, format="%.2f")
    run_btn = st.button("Scanner les value bets maintenant")
with col2:
    st.write("API keys (env vars possibles)")
    theodds_key = st.text_input("THEODDS_API_KEY", THEODDS_API_KEY, type="password")
    footballdata_key = st.text_input("FOOTBALL_DATA_API_KEY", FOOTBALL_DATA_API_KEY, type="password")

if run_btn:
    st.info("Récupération des cotes...")
    try:
        events = fetch_odds(sport_key=sport_choice, regions=region_choice, markets=market_choice)
    except Exception as e:
        st.error(f"Erreur récupération odds: {e}")
        events = []

    rows = []
    alerts = []
    for ev in events:
        teams = ev.get("home_team"), ev.get("away_team")
        commence = ev.get("commence_time")
        bookmakers = ev.get("bookmakers", [])
        if not bookmakers:
            continue

        b0 = bookmakers[0]
        markets = b0.get("markets", [])
        market = markets[0] if markets else {}
        outcomes = market.get("outcomes", [])

        odds_map = {}
        for o in outcomes:
            name = o.get("name")
            price = o.get("price")
            odds_map[name] = price

        home_name = ev.get("home_team")
        away_name = ev.get("away_team")
        dec_home = odds_map.get(home_name) or odds_map.get("Home") or odds_map.get("home") or None
        dec_away = odds_map.get(away_name) or odds_map.get("Away") or odds_map.get("away") or None
        dec_draw = odds_map.get("Draw") or odds_map.get("X") or odds_map.get("draw") or None

        if None in (dec_home, dec_draw, dec_away):
            homes, draws, aways = [], [], []
            for b in bookmakers:
                for m in b.get("markets", []):
                    for o in m.get("outcomes", []):
                        n = o.get("name")
                        p = o.get("price")
                        if n == home_name: homes.append(p)
                        elif n == away_name: aways.append(p)
                        elif n.lower() == "draw" or n in ("X","Draw"): draws.append(p)
                        elif n.lower() == "home": homes.append(p)
                        elif n.lower() == "away": aways.append(p)
            dec_home = np.mean(homes) if homes else dec_home
            dec_draw = np.mean(draws) if draws else dec_draw
            dec_away = np.mean(aways) if aways else dec_away

        if None in (dec_home, dec_draw, dec_away):
            continue

        imp = [implied_prob_from_decimal(dec_home), implied_prob_from_decimal(dec_draw), implied_prob_from_decimal(dec_away)]
        imp_norm = normalize_implied_prob(imp)

        team_home_stats = {"for_avg": 1.4, "against_avg": 1.1}
        team_away_stats = {"for_avg": 1.2, "against_avg": 1.3}
        lam_home, lam_away = estimate_expected_goals(team_home_stats, team_away_stats)
        model_probs = estimate_poisson_probs(lam_home, lam_away)

        # Detect value bets
        value_diffs = [model_probs[i] - imp_norm[i] for i in range(3)]
        max_diff = max(value_diffs)
        max_idx = value_diffs.index(max_diff)
        outcome_labels = ["Home Win", "Draw", "Away Win"]

        if max_diff > threshold:
            alert = {
                "Match": f"{home_name} vs {away_name}",
                "Start": commence,
                "Outcome": outcome_labels[max_idx],
                "Value Diff": round(max_diff, 4),
                "Model Prob": round(model_probs[max_idx],4),
                "Imp Prob": round(imp_norm[max_idx],4),
                "Odds": [dec_home, dec_draw, dec_away][max_idx]
            }
            alerts.append(alert)

        row = {
            "Match": f"{home_name} vs {away_name}",
            "Start": commence,
            "Odds Home": dec_home,
            "Odds Draw": dec_draw,
            "Odds Away": dec_away,
            "Model Prob Home": round(model_probs[0],4),
            "Model Prob Draw": round(model_probs[1],4),
            "Model Prob Away": round(model_probs[2],4),
            "Imp Prob Home": round(imp_norm[0],4),
            "Imp Prob Draw": round(imp_norm[1],4),
            "Imp Prob Away": round(imp_norm[2],4),
            "Value Diff Home": round(value_diffs[0],4),
            "Value Diff Draw": round(value_diffs[1],4),
            "Value Diff Away": round(value_diffs[2],4)
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    st.subheader("Tous les matchs analysés")
    st.dataframe(df)

    if alerts:
        st.subheader("Value bets détectés")
        for a in alerts:
            st.success(f"{a['Match']} - {a['Outcome']} - Value Diff: {a['Value Diff']} - Odds: {a['Odds']}")
    else:
        st.info("Aucun value bet détecté avec ce seuil.")

import fetch_matches
fetch_matches.generate_csv()
# fetch_matches.py

import requests
import pandas as pd
import time

API_KEY = "2af39073b1ebd42a92862f767d33ddc6"
HEADERS = {"X-Auth-Token": API_KEY}
BASE_URL = "https://api.football-data.org/v4"
COMPETITIONS = ["PL", "PD", "SA", "BL1", "FL1"]

def get_matches_today():
    today = pd.Timestamp.now().date().isoformat()
    matches = []

    for comp in COMPETITIONS:
        url = f"{BASE_URL}/competitions/{comp}/matches?dateFrom={today}&dateTo={today}"
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 200:
            data = res.json().get("matches", [])
            for match in data:
                matches.append({
                    "HomeTeam": match["homeTeam"]["name"],
                    "AwayTeam": match["awayTeam"]["name"],
                    "FTR": get_result_short(match)
                })
        time.sleep(1)
    return matches

def get_result_short(match):
    if match["status"] != "FINISHED":
        return None
    home = match["score"]["fullTime"]["home"]
    away = match["score"]["fullTime"]["away"]
    if home > away:
        return "H"
    elif home < away:
        return "A"
    else:
        return "D"

def get_team_form(team_id):
    url = f"{BASE_URL}/teams/{team_id}/matches?limit=5&status=FINISHED"
    res = requests.get(url, headers=HEADERS)
    form = ""
    if res.status_code == 200:
        matches = res.json().get("matches", [])
        for match in matches:
            is_home = match["homeTeam"]["id"] == team_id
            score = match["score"]["fullTime"]
            if not score:
                continue
            home, away = score.get("home"), score.get("away")
            if home is None or away is None:
                continue
            if (is_home and home > away) or (not is_home and away > home):
                form += "W"
            elif home == away:
                form += "D"
            else:
                form += "L"
    return form[:5]

def enrich_forms(matches):
    team_ids = {}
    for match in matches:
        for team in [match["HomeTeam"], match["AwayTeam"]]:
            if team not in team_ids:
                res = requests.get(f"{BASE_URL}/teams?name={team}", headers=HEADERS)
                if res.status_code == 200:
                    team_ids[team] = res.json().get("teams", [{}])[0].get("id", None)
                time.sleep(1)

    enriched = []
    for match in matches:
        home_id = team_ids.get(match["HomeTeam"])
        away_id = team_ids.get(match["AwayTeam"])
        if home_id and away_id:
            match["HForm"] = get_team_form(home_id)
            match["AForm"] = get_team_form(away_id)
            enriched.append(match)
            time.sleep(1)
    return enriched

def generate_csv():
    matches = get_matches_today()
    enriched = enrich_forms(matches)
    df = pd.DataFrame(enriched)
    df.to_csv("matches_today_form.csv", index=False)
    print("✅ Fichier généré automatiquement !")

if __name__ == "__main__":
    generate_csv()
    with st.spinner("Chargement des matchs en cours..."):
    fetch_matches.generate_csv()

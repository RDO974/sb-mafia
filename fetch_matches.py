
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
        if res.ok:
            for m in res.json().get("matches", []):
                matches.append({
                    "HomeTeam": m["homeTeam"]["name"],
                    "AwayTeam": m["awayTeam"]["name"],
                    "FTR": get_result_short(m)
                })
        time.sleep(1)
    return matches

def get_result_short(m):
    if m.get("status") != "FINISHED":
        return None
    home = m["score"]["fullTime"]["home"] or 0
    away = m["score"]["fullTime"]["away"] or 0
    if home > away: return "H"
    if home < away: return "A"
    return "D"

def get_team_form(team_id):
    url = f"{BASE_URL}/teams/{team_id}/matches?limit=5&status=FINISHED"
    res = requests.get(url, headers=HEADERS)
    form = ""
    if res.ok:
        for m in res.json().get("matches", []):
            is_home = (m["homeTeam"]["id"] == team_id)
            sc = m["score"]["fullTime"]
            if sc and sc.get("home") is not None and sc.get("away") is not None:
                if (is_home and sc["home"] > sc["away"]) or (not is_home and sc["away"] > sc["home"]):
                    form += "W"
                elif sc["home"] == sc["away"]:
                    form += "D"
                else:
                    form += "L"
    return form[:5].ljust(5, "N")

def enrich_forms(matches):
    enriched = []
    team_ids = {}
    for m in matches:
        for t in (m["HomeTeam"], m["AwayTeam"]):
            if t not in team_ids:
                res = requests.get(f"{BASE_URL}/teams", headers=HEADERS, params={"name": t})
                if res.ok and res.json().get("teams"):
                    team_ids[t] = res.json()["teams"][0]["id"]
                else:
                    team_ids[t] = None
                time.sleep(1)
    for m in matches:
        hid = team_ids.get(m["HomeTeam"])
        aid = team_ids.get(m["AwayTeam"])
        if hid and aid:
            m["HForm"] = get_team_form(hid)
            m["AForm"] = get_team_form(aid)
            enriched.append(m)
            time.sleep(1)
    return enriched

def generate_csv():
    matches = get_matches_today()
    if not matches:
        print("Aucun match aujourd'hui.")
        return
    df = pd.DataFrame(enrich_forms(matches))
    df.to_csv("matches_today_form.csv", index=False)
    print("✅ matches_today_form.csv généré")

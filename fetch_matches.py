import pandas as pd
from datetime import datetime

def generate_csv():
    # Exemple simulé de matchs du jour avec formes
    data = {
        "HomeTeam": ["Team A", "Team B", "Team C"],
        "AwayTeam": ["Team D", "Team E", "Team F"],
        "HForm": ["WWDWL", "LDDWW", "WLWLW"],
        "AForm": ["LDWDL", "WWLLD", "DLWLW"],
        "FTR": ["H", "A", "D"]
    }

    df = pd.DataFrame(data)
    df.to_csv("matches_today_form.csv", index=False)

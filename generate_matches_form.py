import pandas as pd

# Exemple de données simulées (tu peux remplacer plus tard par une API)
data = {
    'HForm': ['WWDLW', 'LLDWW', 'WLDWL'],
    'AForm': ['LDLWW', 'WWLLD', 'DDDWL'],
    'FTR': ['H', 'A', 'D']
}

# Création d'un DataFrame
df = pd.DataFrame(data)

# Sauvegarde dans un fichier CSV
df.to_csv('matches_today_form.csv', index=False)
print("✅ Fichier matches_today_form.csv généré avec succès")

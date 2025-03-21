import http.client
import json

conn = http.client.HTTPSConnection("anime-db.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "1d9893af29mshbffda0f261e66d4p1f8714jsn270e044eef5c",
    'x-rapidapi-host': "anime-db.p.rapidapi.com"
}

conn.request("GET", "/anime?page=1&size=100000000", headers=headers)

res = conn.getresponse()
data = res.read()

# Convertir en dictionnaire
anime_dict = json.loads(data.decode("utf-8"))

for e in anime_dict:
    del e["link"]
    del e["image"]
    del e["thumb"]
    del e["hasEpisode"]
    del e["hasRanking"]

# Écrire dans un fichier JSON
with open("anime_data.json", "w", encoding="utf-8") as json_file:
    json.dump(anime_dict, json_file, ensure_ascii=False, indent=4)





import pandas as pd

df = pd.read_csv("datas/anime.csv", sep=",", quotechar='"', quoting=1)

df["format"] = "anime"

# Sauvegarder le fichier nettoyé
df.to_csv("datas/anime.csv", index=False, sep=",", quotechar='"', quoting=1)




try:
    df = pd.read_csv("datas/film_original.csv", sep=",", quotechar='"', quoting=1)

    # Garder uniquement les lignes où 'adult' est False
    df = df[df["adult"] == False]

    df["format"] = "movie"

    # Supprimer les colonnes inutiles
    df = df.drop(columns=["adult", "vote_count", "revenue", "backdrop_path", "budget", "homepage", "imdb_id", "original_language", "popularity", "poster_path", "production_countries", "spoken_languages"])

    # Renommer la colonne
    df = df.rename(columns={"overview": "synopsis"})

    # Sauvegarder le fichier nettoyé
    df.to_csv("datas/film.csv", index=False, sep=",", quotechar='"', quoting=1)
except FileNotFoundError:
    print("Erreur : Le fichier 'datas/film_original.csv' est introuvable. Téléchargez le sur Kaggle")
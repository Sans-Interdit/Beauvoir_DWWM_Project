import http.client
import json

# conn = http.client.HTTPSConnection("anime-db.p.rapidapi.com")

# headers = {
#     'x-rapidapi-key': "1d9893af29mshbffda0f261e66d4p1f8714jsn270e044eef5c",
#     'x-rapidapi-host': "anime-db.p.rapidapi.com"
# }

# conn.request("GET", "/anime?page=1&size=100000000", headers=headers)

# res = conn.getresponse()
# data = res.read()

# # Convertir en dictionnaire
# anime_dict = json.loads(data.decode("utf-8"))

# # Écrire dans un fichier JSON
# with open("anime_data.json", "w", encoding="utf-8") as json_file:
#     json.dump(anime_dict, json_file, ensure_ascii=False, indent=4)

# print("Les données ont été enregistrées dans 'anime_data.json'.")

# with open("anime_data.json", "r", encoding="utf-8") as json_file:
#     anime_dict = json_file.read()
#     anime_dict = json.loads(anime_dict)

#     for e in anime_dict:
#         del e["link"]
#         del e["image"]
#         del e["thumb"]
#         del e["hasEpisode"]
#         del e["hasRanking"]

# # Écrire dans un fichier JSON
# with open("anime_data.json", "w", encoding="utf-8") as json_file:
#     json.dump(anime_dict, json_file, ensure_ascii=False, indent=4)

# print("Les données ont été enregistrées dans 'anime_data.json'.")







# import http.client

# conn = http.client.HTTPSConnection("imdb-top-1000-movies-series.p.rapidapi.com")

# headers = {
#     'x-rapidapi-key': "1d9893af29mshbffda0f261e66d4p1f8714jsn270e044eef5c",
#     'x-rapidapi-host': "imdb-top-1000-movies-series.p.rapidapi.com"
# }

# conn.request("GET", "/list/9", headers=headers)

# res = conn.getresponse()
# data = res.read()

# with open("original_film_data.json", "r", encoding="utf-8") as json_file:
#     film_list = json_file.read()
#     film_list = json.loads(film_list)

#     for e in film_list:
#         del e["Released_Year"]
#         del e["Poster_Link"]
#         del e["Certificate"]
#         del e["Runtime"]
#         del e["IMDB_Rating"]
#         del e["Meta_score"]
#         del e["No_of_Votes"]
#         del e["Gross"]
#         e["synopsis"] = e["Overview"]
#         e["genres"] = e["Genre"]
#         e["title"] = e["Series_Title"]
#         del e["Overview"]
#         del e["Genre"]
#         del e["Series_Title"]

# # Écrire dans un fichier JSON
# with open("film_data.json", "w", encoding="utf-8") as json_file:
#     json.dump(film_list, json_file, ensure_ascii=False, indent=4)

















# import pandas as pd

# df = pd.read_csv("datas/film_original.csv", sep=",", quotechar='"', quoting=1)

# # Garder uniquement les lignes où 'adult' est False
# df = df[df["adult"] == False]

# df["format"] = "movie"

# # Supprimer les colonnes inutiles
# df = df.drop(columns=["adult", "vote_count", "revenue", "backdrop_path", "budget", "homepage", "imdb_id", "original_language", "popularity", "poster_path", "production_countries", "spoken_languages"])

# # Renommer la colonne
# df = df.rename(columns={"overview": "synopsis"})

# # Sauvegarder le fichier nettoyé
# df.to_csv("datas/film.csv", index=False, sep=",", quotechar='"', quoting=1)




 


import pandas as pd

df = pd.read_csv("datas/anime.csv", sep=",", quotechar='"', quoting=1)

df["format"] = "anime"

# Sauvegarder le fichier nettoyé
df.to_csv("datas/anime.csv", index=False, sep=",", quotechar='"', quoting=1)
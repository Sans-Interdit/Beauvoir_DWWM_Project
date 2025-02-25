# import http.client
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




with open("anime_data.json", "r", encoding="utf-8") as json_file:
    anime_dict = json_file.read()
    anime_dict = json.loads(anime_dict)

    for e in anime_dict:
        del e["link"]
        del e["image"]
        del e["thumb"]
        del e["hasEpisode"]
        del e["hasRanking"]

# Écrire dans un fichier JSON
with open("anime_data.json", "w", encoding="utf-8") as json_file:
    json.dump(anime_dict, json_file, ensure_ascii=False, indent=4)

print("Les données ont été enregistrées dans 'anime_data.json'.")
# import http.client
# import json

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

# for e in anime_dict:
#     del e["link"]
#     del e["image"]
#     del e["thumb"]
#     del e["hasEpisode"]
#     del e["hasRanking"]

# # Écrire dans un fichier JSON
# with open("anime_data.json", "w", encoding="utf-8") as json_file:
#     json.dump(anime_dict, json_file, ensure_ascii=False, indent=4)



import pandas as pd
from googletrans import Translator
import time
import asyncio

translator = Translator()

df = pd.read_csv("datas/film_translated_subset.csv", sep=",", quotechar='"', quoting=1)

subset_size = len(df)
df_subset = df.iloc[:subset_size]

df_subset.loc[:, "synopsis"] = df_subset["synopsis"].fillna("").astype(str)

# Fonction asynchrone pour traduire un batch
async def translate_batch(batch):
    return await translator.translate(batch, src="en", dest="fr")

async def main():
    translated_texts = []
    batch_size = 50  # Taille du batch

    for i in range(0, len(df_subset), batch_size):
        try:
            print(i)
            batch = df_subset["synopsis"].iloc[i:i+batch_size].tolist()  # Liste des textes à traduire
            
            # Appel asynchrone
            translations = await translate_batch(batch)

            for translation in translations:
                translated_texts.append(translation.text)

        except Exception as e:
            print(f"Exception à l'index {i}: {e}")
    print(f"taille attendue: {subset_size}, taille obtenue: {len(translated_texts)}")

    df.loc[df.index[:subset_size], "synopsis"] = translated_texts

    # Sauvegarde du fichier mis à jour
    df.to_csv("datas/anime_translated.csv", index=False, sep=",", quotechar='"', quoting=1)
    
    print("Traduction terminée et sauvegardée dans 'datas/anime_translated.csv'.")

# Lancer la fonction principale asynchrone
asyncio.run(main())




# try:
#     df = pd.read_csv("datas/film_original.csv", sep=",", quotechar='"', quoting=1)

#     # Garder uniquement les lignes où 'adult' est False
#     df = df[df["adult"] == False]

#     df["format"] = "film"

#     # Supprimer les colonnes inutiles
#     df = df.drop(columns=["adult", "vote_count", "revenue", "backdrop_path", "budget", "homepage", "imdb_id", "original_language", "popularity", "poster_path", "production_countries", "spoken_languages"])

#     # Renommer la colonne
#     df = df.rename(columns={"overview": "synopsis"})

#     # Sauvegarder le fichier nettoyé
#     df.to_csv("datas/film.csv", index=False, sep=",", quotechar='"', quoting=1)
# except FileNotFoundError:
#     print("Erreur : Le fichier 'datas/film_original.csv' est introuvable. Téléchargez le sur Kaggle")




# df = pd.read_csv("datas/film_translated.csv", sep=",", quotechar='"', quoting=1)

# df_subset = df.iloc[:21447]

# df_subset.to_csv("datas/film_translated_subset.csv", index=False, sep=",", quotechar='"', quoting=1)
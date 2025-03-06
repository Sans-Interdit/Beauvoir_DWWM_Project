import json
from qdrant_client import models
import numpy as np
from .recommend import client, COLLECTION_NAME, model
import csv

def create_collection():
    if client.collection_exists(COLLECTION_NAME):
        confirmation = input("Are you sure you want to recreate the collection? [y/N]")

        if not confirmation or confirmation[0].lower() != "y":
            return

        client.delete_collection(COLLECTION_NAME)

    vector_size = model.get_sentence_embedding_dimension()
    vector_names = [
        "title",
        # "alternativeTitles",
        "synopsis",
        ]

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config={
            vector_name: models.VectorParams(
                size=vector_size,
                distance=models.Distance.COSINE,
            )
            for vector_name in vector_names
        },
    )

def encode_work(work):
    # altTitle = work.get("alternativeTitles")
    # if altTitle:
    #     altTitle = altTitle.split(", ")
    #     altTitle.append(work["title"])
    #     vectors = {
    #         "title": np.average([model.encode(title) for title in altTitle], axis=0).tolist(),
    #         "synopsis": model.encode(work["synopsis"]),
    #     }

    vectors = {
        "title": model.encode(work["title"]),
        "synopsis": model.encode(work["synopsis"]),
    }

    return models.PointStruct(
        id=int(work["id"]),
        payload=work,
        vector=vectors,
    )


if __name__ == "__main__":
    # create_collection()

    with open("film.csv", mode="r", encoding="utf-8") as file:
        film_liste = list(csv.DictReader(file))
    # with open("film_data.json", "r", encoding="utf-8") as json_file:
    #     works_list = json.load(json_file)
    film_liste = film_liste[:len(film_liste) // 2]

    start = 0
    end = len(film_liste)
    step = 100

    for i in range(start, end, step):
        batch = film_liste[i : i + step]
        print(f"Uploading batch {i // step} of {len(film_liste) // step}")
        points = []
        for work in batch:
            p = encode_work(work)  # Mise à jour explicite de p
            points.append(p)
        print(f"Uploading {len(points)} points")
        try:
            response = client.upload_points(collection_name=COLLECTION_NAME, points=points)
            print(f"Upload successful for batch {i // step}: {response}")
        except Exception as e:
            print(f"Error uploading points: {e}")

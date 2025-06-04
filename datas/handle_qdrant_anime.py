from qdrant_client import models
from back.recommend import client, COLLECTION_NAME, model
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


def encode_works(works):
    titles = [work["title"] for work in works]
    synopses = [work["synopsis"] for work in works]

    for work in works:
        work["genres"] = work["genres"].split(", ")

    # Encodage par lot (batch processing)
    encoded_titles = model.encode(
        titles, batch_size=32, device="cuda", convert_to_numpy=True
    )
    encoded_synopses = model.encode(
        synopses, batch_size=32, device="cuda", convert_to_numpy=True
    )

    # Construction des objets PointStruct
    encoded_works = [
        models.PointStruct(
            id=int(work["_id"]),
            payload=work,
            vector={"title": encoded_titles[i], "synopsis": encoded_synopses[i]},
        )
        for i, work in enumerate(works)
    ]

    return encoded_works


def remove_outdated_offers(valid_ids):
    """Supprime les offres de la base vectorielle qui ne sont plus valides."""
    try:
        # Récupérer tous les IDs dans la base vectorielle
        result = client.scroll(collection_name=COLLECTION_NAME, limit=None)
        
        if isinstance(result, tuple):
            records = result[0]  # on extrait la liste des Record si elle est dans un tuple
        else:
            records = result  # sinon c'est déjà une liste

        db_ids = {record.id for record in records}

        # Identifier les IDs obsolètes
        outdated_ids = list(db_ids - set(valid_ids))
        print(outdated_ids)
        if not outdated_ids:
            print("Aucune offre obsolète à supprimer.")
            return

        # Supprimer les points obsolètes
        response = client.delete(collection_name=COLLECTION_NAME, ids=outdated_ids)
        print(f"Offres obsolètes supprimées : {len(outdated_ids)}")

    except Exception as e:
        print(f"Erreur lors de la suppression des offres obsolètes : {e}")

if __name__ == "__main__":
    create_collection()

    with open("datas/anime_translated.csv", mode="r", encoding="utf-8") as file:
        film_liste = list(csv.DictReader(file))

    start = 0
    end = len(film_liste)
    step = 1000

    for i in range(start, end, step):
        batch = film_liste[i : i + step]
        print(f"Uploading batch {i // step} of {len(film_liste) // step}")
        points = encode_works(batch)
        print(f"Uploading {len(points)} points")
        try:
            response = client.upload_points(
                collection_name=COLLECTION_NAME, points=points
            )
            print(f"Upload successful for batch {i // step}: {response}")
        except Exception as e:
            print(f"Error uploading points: {e}")
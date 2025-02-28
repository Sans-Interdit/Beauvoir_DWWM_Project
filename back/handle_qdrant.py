import json
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models
import numpy as np

CLIENT_CONFIG = {
    "url": "http://localhost:6333",
    "api_key": "test",
}

model = SentenceTransformer('all-MiniLM-L6-v2')
client = QdrantClient(**CLIENT_CONFIG)
COLLECTION_NAME = "test"


def create_collection():
    if client.collection_exists(COLLECTION_NAME):
        confirmation = input("Are you sure you want to recreate the collection? [y/N]")

        if not confirmation or confirmation[0].lower() != "y":
            return

        client.delete_collection(COLLECTION_NAME)

    vector_size = model.get_sentence_embedding_dimension()
    vector_names = [
        "title",
        "alternativeTitles",
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
    altTitle = work["alternativeTitles"]
    vectors = {
        "title": model.encode(work["title"]),
        "alternativeTitles": (
            np.average([model.encode(title) for title in altTitle], axis=0).tolist()
            if altTitle else np.zeros(model.encode(work["title"]).shape).tolist()
        ),
        "synopsis": model.encode(work["synopsis"]),
    }

    return models.PointStruct(
        id=int(work["_id"]),
        payload=work,
        vector=vectors,
    )

if __name__ == "__main__":
    # create_collection()


    with open("anime_data.json", "r", encoding="utf-8") as json_file:
        works_list = json.load(json_file)

    start = 0
    end = len(works_list)
    step = 100

    for i in range(start, end, step):
        batch = works_list[i : i + step]
        print(f"Uploading batch {i // step} of {len(works_list) // step}")
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

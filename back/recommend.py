from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
import numpy as np

client = QdrantClient(
    url="http://localhost:6333",
    api_key= "test",
)
COLLECTION_NAME = "works"
model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
model.to('cuda')

def searchWorks(criterias):
    prefetch = create_prefetch(criterias)
    hits = client.query_points(
        collection_name=COLLECTION_NAME,
        prefetch=prefetch,
        query=models.FusionQuery(fusion=models.Fusion.DBSF),
        with_payload=True,
        with_vectors=True,
        limit=50
    )
    for hit in hits.points:
        score = hit.score  # Remplacez 'score' par l'attribut correct si nécessaire
        print(f"Point: {hit.payload["title"]}, Score: {score}")
    results = [point.payload for point in hits.points]

    return results


def create_prefetch(criterias):
    criteria_fields = [
        "title",
        "key_words",
    ]

    criterias = {
        "key_words": ["arrogant", "warrior", "god"],
        "genre": ["Documentary", "Science Fiction"]
    }

    filter_value = None

    format = criterias.get("format")
    if format:
        filter_value = models.Filter(
            should=[
                models.FieldCondition(
                    key="format",
                    match=models.MatchValue(value=format, boost=2.0)
                )
            ]
        )

    criteria_vectors = {}
    for possible_field in criteria_fields:
        field = criterias.get(possible_field)
        if field:
            if possible_field == "key_words":
                criteria_vectors["synopsis"] = np.mean(model.encode(field), axis=0)
            else:
                criteria_vectors[possible_field] = model.encode(field)

    if not criteria_vectors:
        return models.Prefetch(filter=filter_value, limit=50)
    elif not filter_value:
        return [
            models.Prefetch(
                query=vector_value, using=vector_name, limit=50
            )
            for vector_name, vector_value in criteria_vectors.items()
        ]
    else:
        return [
            models.Prefetch(
                query=vector_value, using=vector_name,filter=filter_value, limit=50
            )
            for vector_name, vector_value in criteria_vectors.items()
        ]
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer

client = QdrantClient(
    url="http://localhost:6333",
    api_key= "test",
)
COLLECTION_NAME = "all-works"
model = SentenceTransformer('all-MiniLM-L6-v2')
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
    
    results = [point.payload for point in hits.points]

    return results


def create_prefetch(criterias):
    criteria_fields = [
        "title",
        "key_words",
    ]

    criteria_vectors = {}
    for possible_field in criteria_fields:
        field = criterias.get(possible_field)
        if field:
            if possible_field == "key_words":
                criteria_vectors["synopsis"] = model.encode(" ".join(field))
            else:
                criteria_vectors[possible_field] = model.encode(field)
    # if not criteria_vectors:
    #     return [models.Prefetch()]

    return [
        models.Prefetch(
            query=vector_value, using=vector_name, limit=50 # filter=filter_value,
        )
        for vector_name, vector_value in criteria_vectors.items()
    ]
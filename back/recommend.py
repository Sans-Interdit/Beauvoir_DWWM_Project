from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
import numpy as np

client = QdrantClient(
    url="http://localhost:6333",
    api_key="test",
)
COLLECTION_NAME = "all_works"
model = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")
model.to("cuda")


def searchWorks(criterias):
    """
    Searches for audiovisual works matching given criteria in a Qdrant vector database.

    Encodes text-based criteria into vectors and applies optional filtering (e.g. by format).
    Uses vector similarity to retrieve the most relevant results.

    Args:
        criterias (dict): A dictionary with criteria such as 'key_words', 'title', or 'format'.

    Returns:
        list: A list of result payloads (matching works).
    """
    prefetch = create_prefetch(criterias)
    hits = client.query_points(
        collection_name=COLLECTION_NAME,
        prefetch=prefetch,
        query=models.FusionQuery(fusion=models.Fusion.DBSF),
        with_payload=True,
        with_vectors=True,
        limit=50,
    )
    for hit in hits.points:
        score = hit.score  # Remplacez 'score' par l'attribut correct si nécessaire
        print(f"Point: {hit.payload["title"]}, Score: {score}")
    results = [point.payload for point in hits.points]

    return results


def create_prefetch(criterias):
    """
    Builds the prefetch object used for querying the Qdrant vector database.

    Encodes fields into vectors using a sentence transformer model and applies filtering
    if a format is specified. Can return a list of vector-based prefetch objects or
    include a format-based filter.

    Args:
        criterias (dict): A dictionary with possible keys: 'title', 'key_words', and 'format'.

    Returns:
        Union[models.Prefetch, list[models.Prefetch]]: Prefetch query configuration.
    """
    criteria_fields = [
        "title",
        "key_words",
    ]

    # criterias = {
    #     "key_words": ["arrogant", "warrior", "god"],
    #     "genre": ["Documentary", "Science Fiction"]
    # }

    filters = []

    format = criterias.get("format")
    if format:
        filters.append(
            models.FieldCondition(
                key="format", match=models.MatchValue(value=format)  # , boost=2.0
            )
        )

    genres = criterias.get("genre")
    if genres:
        filters.extend([
            models.FieldCondition(
                key="genres", match=models.MatchValue(value=genre.strip())  # , boost=2.0
            ) for genre in genres
        ])

    if filters:
        filter_value = models.Filter(should=filters)
    else:
        filter_value = None


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
            models.Prefetch(query=vector_value, using=vector_name, limit=50)
            for vector_name, vector_value in criteria_vectors.items()
        ]
    else:
        return [
            models.Prefetch(
                query=vector_value, using=vector_name, filter=filter_value, limit=50
            )
            for vector_name, vector_value in criteria_vectors.items()
        ]

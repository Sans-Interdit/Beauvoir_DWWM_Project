from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
import numpy as np

# Initialize Qdrant client for vector similarity search
client = QdrantClient(
    url="http://localhost:6333",  # Qdrant service URL
    api_key="test",                # API key for authentication
)
COLLECTION_NAME = "all-works"  # Name of the Qdrant collection storing all works

# Load multilingual sentence transformer model for vector encoding
model = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")
# model.to("cuda")  # Move model to GPU for faster encoding


def searchWorks(criterias):
    """
    Searches for audiovisual works matching given criteria in a Qdrant vector database.

    Encodes text-based criteria into vectors and applies optional filtering (e.g., by format or genres).
    Uses vector similarity to retrieve the most relevant results.

    Args:
        criterias (dict): A dictionary with search criteria such as 'key_words', 'title', 'genres', or 'format'.

    Returns:
        list: A list of result payloads (matching works).
    """
    # Build prefetch configuration based on criteria
    prefetch = create_prefetch(criterias)

    # Execute a fusion query with DBSF algorithm, fetching payload and vector for each hit
    hits = client.query_points(
        collection_name=COLLECTION_NAME,
        prefetch=prefetch,
        query=models.FusionQuery(fusion=models.Fusion.DBSF),
        with_payload=True,
        with_vectors=True,
        limit=50,
    )

    # Extract and return only the payloads (metadata of works)
    results = [point.payload for point in hits.points]
    return results


def create_prefetch(criterias):
    """
    Builds the prefetch object used for querying the Qdrant vector database.

    Encodes specified fields into vectors using the transformer model and applies
    optional filters if 'format' or 'genres' criteria are provided.

    Args:
        criterias (dict): A dictionary with possible keys: 'title', 'key_words', 'genres', and 'format'.

    Returns:
        Union[models.Prefetch, list[models.Prefetch]]: Prefetch query configuration for vector and filter.
    """
    # Fields to encode into vectors
    criteria_fields = [
        "title",
        "key_words",
    ]

    filters = []  # List of FieldCondition objects for filtering payloads

    # Add format filter if specified
    format_value = criterias.get("format")
    if format_value:
        filters.append(
            models.FieldCondition(
                key="format", match=models.MatchValue(value=format_value.lower())
            )
        )

    # Add genre filters for each specified genre
    genres = criterias.get("genres")
    if genres:
        filters.extend([
            models.FieldCondition(
                key="genres",
                match=models.MatchValue(value=genre.strip().lower())
            ) for genre in genres
        ])

    # Combine filters into a single Filter object if any conditions exist
    filter_value = models.Filter(must=filters) if filters else None

    # Encode text criteria into vectors
    criteria_vectors = {}
    for possible_field in criteria_fields:
        field_content = criterias.get(possible_field)
        if field_content:
            if possible_field == "key_words":
                # Compute mean vector for list of keywords
                criteria_vectors["synopsis"] = np.mean(model.encode(field_content), axis=0)
            else:
                # Encode single-field text directly
                criteria_vectors[possible_field] = model.encode(field_content)

    # If no vectors to query, return only filtering prefetch
    if not criteria_vectors:
        return models.Prefetch(filter=filter_value, limit=50)
    else:
        return [
            models.Prefetch(
                query=vector_value,
                using=vector_name,
                filter=filter_value,
                limit=50
            )
            for vector_name, vector_value in criteria_vectors.items()
        ]

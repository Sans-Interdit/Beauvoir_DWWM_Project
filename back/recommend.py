from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
import numpy as np
import random
import json
import torch
print(torch.__version__)
print(torch.version.cuda)  # Doit afficher une version (ex: "11.8"), sinon CUDA n'est pas dispo.



client = QdrantClient(
    url="http://localhost:6333",
    api_key= "test",
)
COLLECTION_NAME = "works"
model = SentenceTransformer('all-MiniLM-L6-v2')
if torch.cuda.is_available():
    total_memory = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)  # En Go
    print(f"VRAM disponible : {total_memory:.2f} Go")
else:
    print("non")

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
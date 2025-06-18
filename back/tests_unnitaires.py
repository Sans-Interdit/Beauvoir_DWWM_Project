# test_prompts.py
# from llm_calls import (
#     determine_prompt_type,
#     determine_criterias,
# )  # Assurez-vous que ce fichier est correct
# import json
# from recommend import client, COLLECTION_NAME, model, searchWorks
# import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def test_determine_prompt_type1():
    try:
        prompt = {
            "role": "user",
            "content": "Je cherche un film avec le personnage de Harley Quinn",
        }
        result = determine_prompt_type(prompt)
        expected_result = "oui"
        assert result.lower() == expected_result
        print("✅ test_determine_prompt_type (cas 1) réussi")

    except AssertionError:
        print("❌ test_determine_prompt_type (cas 1) échoué")


def test_determine_prompt_type2():
    try:
        prompt = {"role": "user", "content": "Je souhaite avoir la météo de demain"}
        result = determine_prompt_type(prompt)
        expected_result = "non"
        assert result.lower() == expected_result
        print("✅ test_determine_prompt_type (cas 2) réussi")

    except AssertionError:
        print("❌ test_determine_prompt_type (cas 2) échoué")


def test_determine_criterias():
    try:
        prompt = {
            "role": "user",
            "content": "Je cherche un film avec le personnage de Harley Quinn",
        }
        result = json.loads(determine_criterias(prompt))
        expected_result = json.loads('{"format": "film","key_words": ["Harley Quinn"]}')
        assert result == expected_result
        print("✅ test_determine_criterias réussi")

    except AssertionError:
        print("❌ test_determine_criterias échoué")


def test_recommendation():
    try:
        criterias = {"format": "film", "key_words": ["Harley Quinn"]}
        result = searchWorks(criterias)
        listTitles = [ele["title"] for ele in result]
        titles_to_check = [
            "Birds of Prey (and the Fantabulous Emancipation of One Harley Quinn)",
            "Batman and Harley Quinn",
            "The Suicide Squad",
        ]
        assert all(title in listTitles for title in titles_to_check)
        print("✅ test_recommendation réussi")

    except AssertionError:
        print("❌ test_determine_criterias échoué")


if __name__ == "__main__":
    # test_determine_prompt_type1()
    # test_determine_prompt_type2()
    # test_determine_criterias()
    # test_recommendation()

    from qdrant_client import QdrantClient, models
    from sentence_transformers import SentenceTransformer
    import numpy as np

    client = QdrantClient(
        url="http://localhost:6333",
        api_key="test",
    )
    COLLECTION_NAME = "all-works"
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
            # print(f"Point: {hit.payload["title"]}, Score: {score}")
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

        genres = criterias.get("genres")
        print(f"Genres: {genres}")
        if genres:
            filters.extend([
                models.FieldCondition(
                    key="genres", 
                    match=models.MatchValue(value=genre.strip())  # , boost=2.0
                ) for genre in genres
            ])
        if filters:
            filter_value = models.Filter(must=filters)
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
            print("popopopopopopopopopopopopopopopopopopo")
            return models.Prefetch(filter=filter_value, limit=50)
        else:
            print(filter_value)
            return [
                models.Prefetch(
                    query=vector_value, using=vector_name, filter=filter_value, limit=50
                )
                for vector_name, vector_value in criteria_vectors.items()
            ]

    print(searchWorks({
          "format": "film",
          "genres": ["romance"],
          "key_words": ["étudiants"]
        }))

    
    # from sentence_transformers import SentenceTransformer
    # print("fjisfp")

    # model = SentenceTransformer("shawhin/distilroberta-ai-job-embeddings")
    # model.to("cuda")
    # model2 = SentenceTransformer("msmarco-distilbert-base-tas-b")
    # model2.to("cuda")
    # print("'iofsoj")
    # a = "RH"
    # b = "Chargé des ressources humaines"

    # va = model.encode(a, device='cuda', convert_to_numpy=True)
    # vb = model.encode(b, device='cuda', convert_to_numpy=True)
    # aa = model2.encode(a, device='cuda', convert_to_numpy=True)
    # ab = model2.encode(b, device='cuda', convert_to_numpy=True)
    # similarity = cosine_similarity([va], [vb])[0, 0]
    # similarityr = cosine_similarity([aa], [ab])[0, 0]

    # # Résultat
    # print(f"Similarité cosinus entre le texte et les mots-clés: {similarity:.4f}")
    # print(f"Similarité cosinus entre le texte et les mots-clés: {similarityr:.4f}")

# test_prompts.py
from llm_calls import (
    determine_prompt_type,
    determine_criterias,
)  # Assurez-vous que ce fichier est correct
import json
from recommend import client, COLLECTION_NAME, model, searchWorks
import numpy as np
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
    test_determine_prompt_type1()
    test_determine_prompt_type2()
    test_determine_criterias()
    test_recommendation()

    # a = "Kaoruko ""Chaos"" Moeta est une jeune artiste de manga qui a de la chance. Elle veut dessiner des mangas sur les lycéens, mais ses storyboards sont fade, son art sans inspiration et ses locaux faibles. Son éditeur inquiet et exaspéré propose une idée: pousser le chaos pour être plus social. Ainsi, par sa recommandation, le chaos entre dans un dortoir pour les artistes mangas féminins. Elle rencontre bientôt les autres résidents: Tsubasa Katsuki, un artiste de manga Shounen; Ruki Irokawa, qui dessine des mangas érotiques populaires auprès des femmes; et Koyume Koizuka, un artiste shoujo qui, comme le chaos, n'a pas encore été sérialisé. Rencontre rapidement une amitié avec ces filles, le chaos trouve une nouvelle inspiration pour son manga et continue de développer sa créativité.  Comic Girls est une vitrine de la vie quotidienne de ces artistes de mangas. Le chaos pourra-t-il enfin faire ses débuts et devenir sérialisé? Aucune des filles ne le savait, mais elles feront toutes de leur mieux pour s'entraider les autres artistes.  [Écrit par MAL REWRITE]"
    # c = "La cinquième saison de la franchise Dokan-Kun. Il a été diffusé dans le programme de variétés \"Dejisuta Teens\""
    # b = "une adolescente mangaka dans un dortoir"

    # va = model.encode(a, batch_size=32, device='cuda', convert_to_numpy=True)
    # vc = model.encode(c, batch_size=32, device='cuda', convert_to_numpy=True)
    # vb = model.encode(b, batch_size=32, device='cuda', convert_to_numpy=True)

    # similarityb = cosine_similarity([va], [vb])[0][0]
    # similarityc = cosine_similarity([vc], [vb])[0][0]

    # # Résultat
    # print(f"Similarité cosinus entre le texte et les mots-clés: {similarityb:.4f}")
    # print(f"Similarité cosinus entre le texte et les mots-clés: {similarityc:.4f}")

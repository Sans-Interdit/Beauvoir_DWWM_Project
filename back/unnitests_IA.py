# test_prompts.py
from llm_calls import determine_prompt_type, determine_criterias  # Assurez-vous que ce fichier est correct
import json

def test_determine_prompt_type():
    try:
        prompt = {"role": "user", "content": "Je cherche un film avec un super héros"}
        result = determine_prompt_type(prompt)
        expected_result = "oui"
        assert result == expected_result
        print("✅ test_determine_prompt_type (cas 1) réussi")

        prompt = {"role": "user", "content": "Je souhaite avoir "}    
        result = determine_prompt_type(prompt)
        expected_result = "non"
        assert result == expected_result
        print("✅ test_determine_prompt_type (cas 2) réussi")
    
    except AssertionError:
        print("❌ test_determine_prompt_type échoué")

def test_determine_criterias():
    try:
        prompt = {"role": "user", "content": "Je veux voir un film d’action, genre science-fiction, avec un titre comme Inception"}
        result = json.loads(determine_criterias(prompt))
        expected_result = json.loads('{"title": "Inception", "format": "film", "key_words": ["action", "science-fiction"]}')
        assert result == expected_result
        print("✅ test_determine_criterias réussi")
    
    except AssertionError:
        print("❌ test_determine_criterias échoué")

if __name__ == "__main__":
    test_determine_prompt_type()
    test_determine_criterias()

import ollama

def determine_prompt_type(prompt):
    metaprompt = {"role":'system', "content" : f"""Une liste d'oeuvres audiovisuelles est présenté à l'utilisateur.
Votre rôle est de determiner si le message de l'utilisateur apporte des précisions concernant l'oeuvres audiovisuelle qu'il recherche.
Ne réponds uniquement par oui ou non."""}
    
    response = ollama.chat(
        model="french_qwen",
        stream=False,
        messages=[metaprompt, prompt],
        options={"temperature": 0.3}
    )

    return response["message"]["content"]

def determine_criterias(prompt):
    metaprompt = {"role":'system', "content" : f"""Votre rôle est de déterminer les critères récherché par l'utilisateur dans son message.
N'y mettez que les critères clairement identifiés.
Ne mettez que les critères explicitement exprimés.
La réponse doit être un JSON valide contenant un ou plusieurs des critères suivants:
- "title": str
- "ranking": float (entre 0 et 1)
- "genres": list[str] (parmi "Action", "Adventure", "Comedy", "Drama", "Fantasy", "Magic", "Mystery", "Psychological", "Romance", "Sci-Fi", "Slice of Life", "Supernatural")
- "episodes": int (nombre d'épisodes total)
- "status": str (parmi "Not yet aired", "Currently Airing", "Finished Airing")
- "type": str (parmi "Anime", "Movie", "Serie")
- "key_words": list (tous les mots clés identifiés dans le message de l'utilisateur)"""}
    
    response = ollama.chat(
        model="french_qwen",
        stream=False,
        messages=[metaprompt, prompt],
        options={"temperature": 0}
    )
    print(response["message"]["content"])
    return response["message"]["content"]
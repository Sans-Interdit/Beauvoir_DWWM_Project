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

def determine_criterias(prompt): # - \"ranking\": float (entre 0 et 1)\n- \"genres\": list[str]\n- \"episodes\": int (nombre d'épisodes total)\n- \"status\": str\n- (étape de publication : en cours, terminé, etc...) 
    metaprompt = {
        "role": "system",
        "content": "Votre rôle est de déterminer les critères recherchés par l'utilisateur dans son message.\n Ne fait jamais par toi même la recommendation.\nLa réponse doit être un JSON valide.\n Ce JSON sera composé d'un; deux ou trois critères uniquement si pertinents.\n\n***Critères :\n- \"title\": str(Titre de L'oeuvre recherché explicitement mentionné)\n- \"format\": str (le type d'oeuvres : anime, série, film)\n- \"key_words\": list[str] (tous les mots clés clairement identifiés)"
    }
    response = ollama.chat(
        model="french_qwen",
        stream=False,
        messages=[metaprompt, prompt],
        options={"temperature": 0}
    )
    print(response["message"]["content"])
    return response["message"]["content"]
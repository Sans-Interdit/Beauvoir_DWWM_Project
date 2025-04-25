import ollama


def determine_prompt_type(prompt):
    """
    Determines whether the user's prompt is requesting a recommendation.

    Sends the prompt to an LLM with specific instructions to identify if the user
    is asking for a recommendation of an anime, movie, or TV show.

    Args:
        prompt (dict): A dictionary representing the user's message, with 'role' and 'content'.

    Returns:
        str: "oui" if the prompt is a recommendation request, "non" otherwise.
    """
    metaprompt = {
        "role": "system",
        "content": f"""Votre rôle est de determiner si le message de l'utilisateur souhaite une recommendation d'oeuvres audiovisuels.
Réponds par oui si l'utilisateur demande une recommendation d'un anime, d'un film ou d'une série, et par non sinon.""",
    }
    response = ollama.chat(
        model="french_qwen",
        stream=False,
        messages=[metaprompt, prompt],
        options={"temperature": 0.3},
    )

    # print(response["message"]["content"])
    return response["message"]["content"]


def determine_criterias(
    prompt,
):  # - \"ranking\": float (entre 0 et 1)\n- \"genres\": list[str]\n- \"episodes\": int (nombre d'épisodes total)\n- \"status\": str\n- (étape de publication : en cours, terminé, etc...)
    """
    Extracts search criteria from the user's message using an LLM.

    The model returns a valid JSON with one to three relevant criteria, if applicable.

    Args:
        prompt (dict): A dictionary representing the user's message.

    Returns:
        str: A JSON-formatted string with extracted criteria such as:
             - "title": str
             - "format": str
             - "key_words": list[str]
    """
    metaprompt = {
        "role": "system",
        "content": """Votre rôle est de déterminer les critères recherchés par l'utilisateur dans son message.
Ne déduit jamais l'oeuvre recherché.
La réponse doit être un JSON parfaitement valide, sans rien d'autre.
Ce JSON sera composé d'un, deux ou trois critères uniquement si pertinents.
***Critères :
 - \"title\": str(Titre de l'œuvre recherché)
 - \"format\": str (le type d'oeuvres : anime, série, film)
 - \"key_words\": list[str] (tous les mots clés clairement identifiés)

Ne détermine \"title\" que si l'utilisateur le demande explicitement.""",
    }
    response = ollama.chat(
        model="french_qwen",
        stream=False,
        messages=[metaprompt, prompt],
        options={"temperature": 0},
    )
    # print(response["message"]["content"])
    return response["message"]["content"]

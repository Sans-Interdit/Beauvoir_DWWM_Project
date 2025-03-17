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
    metaprompt = {
  "role": "system",
  "content": "Votre rôle est de déterminer les critères recherchés par l'utilisateur dans son message.\nN'y mettez que les critères clairement identifiés.\nNe mettez que les critères explicitement exprimés.\nLa réponse doit être un JSON valide contenant un ou plusieurs des critères suivants:\n\n- \"title\": str\n- \"ranking\": float (entre 0 et 1)\n- \"genres\": list[str] (parmi \"Action\", \"Adventure\", \"Comedy\", \"Drama\", \"Fantasy\", \"Magic\", \"Mystery\", \"Psychological\", \"Romance\", \"Sci-Fi\", \"Slice of Life\", \"Supernatural\")\n- \"episodes\": int (nombre d'épisodes total)\n- \"status\": str (parmi \"Not yet aired\", \"Currently Airing\", \"Finished Airing\")\n- \"format\": str (parmi \"anime\", \"film\", \"serie\")\n- \"key_words\": list[str] (tous les mots clés identifiés dans le message de l'utilisateur)\n\n**Règles supplémentaires :**\n- Si l'utilisateur mentionne \"film(s)\", définir \"format\": \"film\".\n- Si l'utilisateur mentionne \"anime(s)\", définir \"format\": \"anime\".\n- Si l'utilisateur mentionne \"série(s)\", définir \"format\": \"serie\".\n- Ne pas inférer de format si ce n'est pas explicitement mentionné."
}

    response = ollama.chat(
        model="french_qwen",
        stream=False,
        messages=[metaprompt, prompt],
        options={"temperature": 0}
    )
    print(response["message"]["content"])
    return response["message"]["content"]
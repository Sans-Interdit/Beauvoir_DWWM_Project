import ollama

# List of supported genres for recommendation criteria
GENRES = [
    "supernatural", "suspense", "slice of life", "gourmet", "avant Garde",
    "action", "Science Fiction", "adventure", "drama", "crime",
    "thriller", "fantasy", "comedy", "romance", "western",
    "mystery", "war", "family", "horror", "music", "history", "documentary"
]


def determine_prompt_type(prompt):
    """
    Determines whether the user's prompt requests a recommendation.

    Sends the prompt to an LLM with instructions to identify if the user
    is asking for a recommendation of an anime, movie, or TV show.

    Args:
        prompt (dict): User message with 'role' and 'content'.

    Returns:
        str: "oui" if requesting recommendation, "non" otherwise.
    """
    # System message instructing the LLM to classify the prompt
    metaprompt = {
        "role": "system",
        "content": (
            "Your role is to determine if the user's message is asking for a recommendation of an audiovisual work."
            ' Reply "oui" if the user requests an anime, movie, or series recommendation, and "non" otherwise.'
        ),
    }
    # Query the LLM and return its classification
    response = ollama.chat(
        model="DWWM",
        stream=False,
        messages=[metaprompt, prompt],
        options={"temperature": 0},
    )

    return response["message"]["content"]


def determine_criterias(prompt):
    """
    Extracts search criteria from the user's message using an LLM.

    The model returns a valid JSON string with up to three relevant criteria.

    Args:
        prompt (dict): User message dict with 'role' and 'content'.

    Returns:
        str: JSON-formatted string containing keys like "title", "format", "genres", or "key_words".
    """
    # System message guiding JSON extraction without surrounding quotes or extra formatting
    metaprompt = {
        "role": "system",
        "content": (
            "Your task is to identify the search criteria in the user's message. "
            "Respond with a perfectly valid JSON containing up to three criteria if relevant:"
            "\n- \"title\": str (exact work title)"
            "\n- \"format\": str (Type: anime, série, film)"
            "\n- \"genres\": list[str] (choose from: " + ", ".join(GENRES) + ")"
            "\n- \"key_words\": list[str] (additional keywords clearly identified)."
            " Only include 'title' if explicitly requested by the user."
        ),
    }
    # Query the LLM for JSON-formatted criteria
    response = ollama.chat(
        model="DWWM",
        stream=False,
        messages=[metaprompt, prompt],
        options={"temperature": 0},
    )

    return response["message"]["content"]


def create_answer(prompt, hits, model):
    """
    Generates a concise recommendation response based on retrieved works.

    Presents up to two works from hits with brief factual details, max 70 words.

    Args:
        prompt (dict): Original user message dict.
        hits (list): List of work payloads (dicts) with metadata.
        model (str): LLM model name to use for reply.

    Returns:
        str: Generated recommendation response.
    """
    # Prepare system message listing top 5 candidate titles for context
    top_titles = [hit["title"] for hit in hits[:5]]
    metaprompt = {
        "role": "system",
        "content": (
            f"The user requested audiovisual recommendations. Here are five top matches: {top_titles}. "
            "Respond with two selections, providing brief accurate information without fabrication, within 70 words."
        ),
    }
    # Query the LLM to generate the final answer
    response = ollama.chat(
        model=model,
        stream=False,
        messages=[metaprompt, prompt],
        options={"temperature": 0.3},
    )

    return response["message"]["content"]
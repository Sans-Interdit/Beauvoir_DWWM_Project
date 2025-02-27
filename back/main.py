from flask import Flask, request, jsonify
from flask_cors import CORS
import ollama
import json
from .llm_calls import determine_prompt_type, determine_criterias
import random

app = Flask("Beauvoir_DWWM_Project")
CORS(app)

if __name__ == "__main__":
    app.run(debug=True)

@app.route("/chat", methods=["POST"])
def chat():
    api_key_send = request.headers.get("X-API-KEY")
    if api_key_send != "W8Su3FyPlm6PxqEnfb6pcKLP3RnonEHH":
        return jsonify({"error": "Unauthorized access"}), 401
    
    prompt = {"role":"user", "content": request.json.get("message")}

    is_about_reco = determine_prompt_type(prompt).lower() == "oui"

    if is_about_reco:
        criterias = determine_criterias(prompt)
        try:
            criterias = json.loads(criterias)
        except json.JSONDecodeError:
            return jsonify({"error": "Error in determine_criterias. Invalid JSON format"}), 400

        
                
    response = ollama.chat(
        model="french_qwen",
        stream=False,
        messages=[prompt],
        options={"temperature": 0.3}
    )

    return jsonify({"message": response["message"]["content"]}), 200

@app.route("/results", methods=["GET"])
def getWorks():
    with open("anime_data.json", "r", encoding="utf-8") as json_file:
        anime_dict = json.load(json_file)

    random.shuffle(anime_dict)  # Mélange la liste

    return jsonify(anime_dict), 200
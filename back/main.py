from flask import Flask, request, jsonify
import os
from flask_cors import CORS
import ollama
import json

app = Flask("Beauvoir_DWWM_Project")
CORS(app)

if __name__ == "__main__":
    app.run(debug=True)

@app.route("/chat", methods=["POST"])
def chat():
    api_key_send = request.headers.get("X-API-KEY")
    if api_key_send != "W8Su3FyPlm6PxqEnfb6pcKLP3RnonEHH":
        return jsonify({"error": "Unauthorized access"}), 401
    
    prompt = [{"role":"user", "content": request.json.get("message")}]

    response = ollama.chat(
        model="french_qwen",
        stream=False,
        messages=prompt,
        options={"temperature": 0.3}
    )
    print(response["message"])
    return jsonify({"message": response["message"]["content"]}), 200

@app.route("/results", methods=["GET"])
def getWorks():
    with open("anime_data.json", "r", encoding="utf-8") as json_file:
        anime_dict = json_file.read()
        anime_dict = json.loads(anime_dict)
    print(anime_dict[:10])
    return jsonify(anime_dict[:20]), 200
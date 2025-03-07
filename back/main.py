from flask import Flask, request, jsonify
from flask_cors import CORS
import ollama
import json
from .llm_calls import determine_prompt_type, determine_criterias
from models.Account import Account, session
from .recommend import searchWorks
import os
from dotenv import load_dotenv
import jwt
from werkzeug.security import check_password_hash
import bcrypt
import datetime

load_dotenv()

app = Flask("Beauvoir_DWWM_Project")
CORS(app, origins=["http://localhost:8000", "http://127.0.0.1:8000"])

if __name__ == "__main__":
    app.run(debug=True)

@app.route("/chat", methods=["POST"])
def chat():
    api_key_send = request.headers.get("X-API-KEY")
    if api_key_send != os.getenv("API_KEY"):
        return jsonify({"error": "Unauthorized access"}), 401
     
    works = None

    prompt = {"role":"user", "content": request.json.get("message")}

    is_about_reco = determine_prompt_type(prompt).lower() == "oui" # Determine if the user is asking for recommendations

    if is_about_reco:
        criterias = determine_criterias(prompt)
        try:
            criterias = json.loads(criterias)
        except json.JSONDecodeError:
            return jsonify({"error": "Error in determine_criterias. Invalid JSON format"}), 400

        works = searchWorks(criterias)

    response = ollama.chat(
        model="DWWM",
        stream=False,
        messages=[prompt],
        options={"temperature": 0.3}
    )

    return jsonify({"message": response["message"]["content"], "works": works}), 200


@app.route("/login", methods=["POST"])
def login():
    api_key_send = request.headers.get("X-API-KEY")
    print(api_key_send, os.getenv("API_KEY"))
    if api_key_send != os.getenv("API_KEY"):
        return jsonify({"error": "Unauthorized access"}), 401
    
    email = request.json.get("email")
    password = request.json.get("password")

    account = session.query(Account).filter_by(email=email, password=password).first()

    if account and bcrypt.checkpw(password.encode('utf-8'), account['password']):
        payload = {
            'user_id': account['id'],
            'username': account['username'],
            'exp': datetime.datetime.now() + datetime.timedelta(hours=1)
        }
        
        token = jwt.encode(payload, os.getenv("CRYPT_KEY"), algorithm='HS256')
        return jsonify({"token": token}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

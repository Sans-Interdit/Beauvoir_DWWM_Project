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
import bcrypt
import datetime
from functools import wraps

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

    password_hashed = password.encode('utf-8')
    account = session.query(Account).filter_by(email=email).first()
    if account and bcrypt.checkpw(password_hashed, account.password.encode('utf-8')):
        return get_logged(account)
    else:
        return jsonify({"error": "Invalid credentials"}), 401
    
def get_logged(account):
    payload = {
        'id': account.id_account,
        'email': account.email,
        'exp': datetime.datetime.now() + datetime.timedelta(hours=1)
    }
    
    token = jwt.encode(payload, os.getenv("CRYPT_KEY"), algorithm='HS256')
    print(token)
    return jsonify({"token": token}), 200

@app.route("/register", methods=["POST"])
def register():
    email = request.json.get("email")
    password = request.json.get('password')

    account = session.query(Account).filter_by(email=email).first()
    if account:
        return jsonify({"message": "Email already used"}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    new_account = Account(email=email, password=hashed_password)
    session.add(new_account)
    session.commit()

    return get_logged(new_account)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorisation")
        print(token)
        if not token:
            return jsonify({"error": "Token is missing"}), 401
        
        try:
            # token = token.split("Bearer ")[1]  # Suppression du préfixe "Bearer "
            data = jwt.decode(token, os.getenv("CRYPT_KEY"), algorithms=["HS256"])
            request.user_id = data["id"]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)

    return decorated

@app.route("/historic", methods=["POST"])
@token_required
def historic():
    account = session.query(Account).filter_by(id_account=request.user_id).first()
    print(account.conversations)
    return jsonify({"error": "Token is missing"}), 200
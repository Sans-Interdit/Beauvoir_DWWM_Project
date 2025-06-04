from flask import Flask, request, jsonify
from flask_cors import CORS
import ollama
import json
from .llm_calls import determine_prompt_type, determine_criterias
from datas.models import Account, session, Conversation, Message, Recommendation, Genre
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
    """
    Handles user interactions with the chatbot.
    Checks the API key, stores the message, determines if it's a recommendation request,
    retrieves recommendations if needed, and generates a response via Ollama.
    """
    api_key_send = request.headers.get("X-API-KEY")
    print(api_key_send, os.getenv("API_KEY"))
    if api_key_send != os.getenv("API_KEY"):
        return jsonify({"error": "Unauthorized access"}), 401

    userMessage = request.json.get("message")
    id = request.json.get("id")

    new_message = Message(id_conversation=id, content=userMessage)
    session.add(new_message)
    session.commit()

    works = None

    prompt = {"role": "user", "content": userMessage+"/no_think"}

    is_about_reco = (
        determine_prompt_type(prompt).lower() == "oui"
    )  # == Does the user want a recommendation ?

    if is_about_reco:
        conv = session.query(Conversation).filter_by(id_conversation=id).first()
        criterias = determine_criterias(prompt)  # Determines the searching criterias of the user from his prompt
        try:
            criterias = json.loads(criterias)
        except json.JSONDecodeError:
            return (
                jsonify({"error": "Error in determine_criterias. Invalid JSON format"}),
                400,
            )

        works = searchWorks(criterias)  # Get the 50 best recommendations from the Qdrant database using the criterias
        # print(works)
        conv.recommendation.oeuvres = works

    response = ollama.chat(
        model="DWWM", stream=False, messages=[prompt], options={"temperature": 0.3}
    )

    response = response["message"]["content"]

    new_message = Message(id_conversation=id, content=response)
    session.add(new_message)
    session.commit()

    return jsonify({"message": response, "works": works}), 200


@app.route("/login", methods=["POST"])
def login():
    """
    Authenticates a user using their email and password.
    Returns a JWT token if the credentials are valid.
    """
    api_key_send = request.headers.get("X-API-KEY")
    if api_key_send != os.getenv("API_KEY"):
        return jsonify({"error": "Unauthorized access"}), 401

    email = request.json.get("email")
    password = request.json.get("password")

    password_hashed = password.encode("utf-8")
    account = session.query(Account).filter_by(email=email).first()
    if account and bcrypt.checkpw(password_hashed, account.password.encode("utf-8")):
        return get_logged(account)
    else:
        return jsonify({"error": "Invalid credentials"}), 401


def get_logged(account):
    """
    Generates a JWT token for an authenticated user account.
    """
    payload = {
        "id": account.id_account,
        "email": account.email,
        "exp": datetime.datetime.now() + datetime.timedelta(hours=1),
    }

    token = jwt.encode(payload, os.getenv("HASH_KEY"), algorithm="HS256")
    return jsonify({"token": token}), 200


@app.route("/register", methods=["POST"])
def register():
    """
    Registers a new user with an email and a hashed password.
    Returns a JWT token upon successful registration.
    """
    email = request.json.get("email")
    password = request.json.get("password")
    age = request.json.get("age")
    country = request.json.get("country")
    gender = request.json.get("gender")
    try:
        account = session.query(Account).filter_by(email=email).first()
        if account:
            print("Email already used")
            return jsonify({"message": "Email already used"}), 400

        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        new_account = Account(
            email=email,
            password=hashed_password,
            age=age,
            country=country,
            gender=gender,
        )
        session.add(new_account)
        session.commit()
    except Exception as e:
        session.rollback()  # Rollback the transaction
        return jsonify({"message": "An error occurred", "error": str(e)}), 500
    return get_logged(new_account)


def token_required(f):
    """
    Decorator that requires JWT authentication.
    Validates the token and checks for expiration.
    """
    print("token")

    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorisation")
        if not token:
            return jsonify({"error": "Token is missing"}), 401

        try:
            data = jwt.decode(token, os.getenv("HASH_KEY"), algorithms=["HS256"])
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
    """
    Retrieves the conversation history of an authenticated user.
    """
    account = session.query(Account).filter_by(id_account=request.user_id).first()
    conversations = [conv.to_dict() for conv in account.conversations]
    return jsonify({"data": conversations}), 200


@app.route("/newconv", methods=["POST"])
@token_required
def newConv():
    """
    Creates a new conversation for an authenticated user.
    """
    account = session.query(Account).filter_by(id_account=request.user_id).first()

    nbr = len(account.conversations) + 1
    new_conversation = Conversation(
        name=f"Conversation {nbr}", id_account=account.id_account
    )
    session.add(new_conversation)
    session.commit()

    new_recommendation = Recommendation(
        id_conversation=new_conversation.id_conversation, oeuvres=[]
    )
    session.add(new_recommendation)
    session.commit()

    new_message = Message(
        id_conversation=new_conversation.id_conversation,
        content="Bonjour, comment puis-je vous aider aujourd'hui?",
    )
    session.add(new_message)
    session.commit()

    a = (
        session.query(Conversation)
        .filter_by(id_conversation=new_conversation.id_conversation)
        .first()
    )
    print(a.recommendation)
    return jsonify({"id": new_conversation.id_conversation}), 200


@app.route("/suppressconv", methods=["DELETE"])
@token_required
def suppressconv():
    """
    Deletes a conversation for an authenticated user.
    """
    id = request.json.get("id")
    conversation = session.query(Conversation).filter_by(id_conversation=id).first()

    if conversation and conversation.id_account == request.user_id:
        session.delete(conversation)
        session.commit()
        return jsonify({"message": "Conversation suppressed"}), 200

    return jsonify({"error": "Conversation not found or access refused"}), 404


@app.route("/suppressacc", methods=["DELETE"])
@token_required
def suppressacc():
    """
    Deletes an authenticated user's account.
    """
    id = request.user_id

    account = session.query(Account).filter_by(id_account=id).first()
    if account:
        session.delete(account)
        session.commit()
        return jsonify({"message": "Account suppressed"}), 200

    return jsonify({"error": "Account not found or access refused"}), 404


@app.route("/getuserinfos", methods=["GET"])
@token_required
def getinfos():
    """
    Retrieves information about an authenticated user.
    """
    account = session.query(Account).filter_by(id_account=request.user_id).first()
    genres = {e.id_genre : e.name for e in account.genres}
    if account:
        return (
            jsonify(
                {
                    "email": account.email,
                    "age": account.age,
                    "country": account.country,
                    "gender": account.gender,
                    "genres": genres,
                }
            ),
            200,
        )
    else:
        return jsonify({"error": "User not found"}), 404


@app.route("/addgenre", methods=["POST"])
@token_required
def addgenre():
    """
    Adds a genre for an authenticated user.
    """
    id = request.user_id
    genre = request.json.get("genre")
    print(genre)
    account = session.query(Account).filter_by(id_account=id).first()
    if not account:
        print("Account not found")
        return jsonify({"error": "User not found"}), 404
    all_genres = session.query(Genre.name).all()
    print([g[0] for g in all_genres])
    genre = session.query(Genre).filter_by(name=genre).first()
    if not genre:
        print("Genre not found")
        return jsonify({"error": "Genre not found"}), 404

    if genre not in account.genres:
        account.genres.append(genre)
        session.commit()
        return (
            jsonify({"message": "Genre added successfully", "id": genre.id_genre}),
            201,
        )
    else:
        return jsonify({"message": "Genre already associated with user"}), 200


@app.route("/suppressgenre", methods=["DELETE"])
@token_required
def suppressgenre():
    """
    Deletes a genre for an authenticated user.
    """
    id = request.user_id
    id_genre = request.json.get("id")
    account = session.query(Account).filter_by(id_account=id).first()
    genre = session.query(Genre).filter_by(id_genre=id_genre).first()
    print(id_genre, genre)
    if not account or not genre:
        return jsonify({"error": "User not found"}), 404
    
    if genre in account.genres:
        account.genres.remove(genre)  # supprime l'association
        session.commit()
        return jsonify({"message": "Genre removed from user"}), 200
    
    else:
        return jsonify({"error": "Genre not associated with user"}), 404


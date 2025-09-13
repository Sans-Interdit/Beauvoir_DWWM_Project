from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from .llm_calls import determine_prompt_type, determine_criterias, create_answer, client
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

# List of valid genres for content filtering
GENRES = ["supernatural", "suspense", "slice of life", 'gourmet', 'avant Garde', 'action', 'Science Fiction', 'adventure',
       'drama', 'crime', 'thriller', 'fantasy', 'comedy', 'romance', 'western', 'mystery', 'war',
       'family', 'horror', 'music', 'history', 'documentary']

@app.route("/chat", methods=["POST"])
def chat():
    """
    Handles user interactions with the chatbot.
    Checks the API key, stores the message, determines if it's a recommendation request,
    retrieves recommendations if needed, and generates a response via Ollama.
    """
    # Validate API key for security
    api_key_send = request.headers.get("X-API-KEY")
    if api_key_send != os.getenv("API_KEY"):
        print(api_key_send, "      ", os.getenv("API_KEY"))
        return jsonify({"error": "Unauthorized access"}), 401

    # Extract request data
    userMessage = request.json.get("message")
    id = request.json.get("id")
    model = request.json.get("model")

    # Store user message in database
    new_message = Message(id_conversation=id, content=userMessage)
    session.add(new_message)
    session.commit()

    works = None

    prompt = {"role": "user", "content": userMessage}

    # Check if user is asking for recommendations
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
        
        # Filter genres to only include valid ones
        genres = criterias.get("genres")
        if genres:
            criterias["genres"] = [genre for genre in criterias["genres"] if genre in GENRES]
        else:
            # If no genres specified, use user's preferred genres from profile
            token = request.headers.get("Authorisation")
            if token:
                try:
                    data = jwt.decode(token, os.getenv("HASH_KEY"), algorithms=["HS256"])
                except jwt.ExpiredSignatureError:
                    data = None                
                except jwt.InvalidTokenError:
                    data = None
                if data:
                    account = session.query(Account).filter_by(id_account=data["id"]).first()
                    criterias["genres"] = [genre.name for genre in account.genres]
        
        # Search for works based on criteria
        works = searchWorks(criterias)  # Get the 50 best recommendations from the Qdrant database using the criterias
        conv.recommendation.oeuvres = works
        session.commit()

    # Generate response based on whether it's a recommendation or general chat
    if is_about_reco:
        response = create_answer(prompt, works, model)
    else:
        response = client.chat(
            model=model, stream=False, messages=[prompt], options={"temperature": 0.3}
        )
        response = response["message"]["content"]

    # Store bot response in database
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
    # Validate API key
    api_key_send = request.headers.get("X-API-KEY")
    if api_key_send != os.getenv("API_KEY"):
        return jsonify({"error": "Unauthorized access"}), 401

    email = request.json.get("email")
    password = request.json.get("password")

    # Verify password against stored hash
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
    # Create JWT payload with expiration time
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
        # Check if email is already registered
        account = session.query(Account).filter_by(email=email).first()
        if account:
            return jsonify({"message": "Email already used"}), 400

        # Hash password for secure storage
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        # Create new account
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

    @wraps(f)
    def decorated(*args, **kwargs):
        # Extract and validate JWT token
        token = request.headers.get("Authorisation")
        if not token:
            return jsonify({"error": "Token is missing"}), 401

        try:
            # Decode and validate token
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
    # Get user account and return conversation history
    account = session.query(Account).filter_by(id_account=request.user_id).first()
    conversations = [conv.to_dict() for conv in account.conversations]
    return jsonify({"data": conversations}), 200


@app.route("/newconv", methods=["POST"])
@token_required
def newConv():
    """
    Creates a new conversation for an authenticated user.
    """
    # Retrieve the authenticated user's account
    account = session.query(Account).filter_by(id_account=request.user_id).first()

    # Determine the new conversation number based on existing ones
    nbr = len(account.conversations) + 1
    # Create a new Conversation instance with a default name
    new_conversation = Conversation(
        name=f"Conversation {nbr}", id_account=account.id_account
    )
    session.add(new_conversation)
    session.commit()

    # Initialize an empty Recommendation linked to the new conversation
    new_recommendation = Recommendation(
        id_conversation=new_conversation.id_conversation, oeuvres=[]
    )
    session.add(new_recommendation)
    session.commit()

    # Add a default welcome message to the conversation
    new_message = Message(
        id_conversation=new_conversation.id_conversation,
        content="Bonjour, comment puis-je vous aider aujourd'hui?",
    )
    session.add(new_message)
    session.commit()

    # Retrieve the conversation to confirm recommendation was linked correctly
    a = (
        session.query(Conversation)
        .filter_by(id_conversation=new_conversation.id_conversation)
        .first()
    )
    # Return the new conversation ID to the client
    return jsonify({"id": new_conversation.id_conversation}), 200


@app.route("/suppressconv", methods=["DELETE"])
@token_required
def suppressconv():
    """
    Deletes a conversation for an authenticated user.
    """
    # Extract conversation ID from request body
    conv_id = request.json.get("id")
    # Fetch the conversation from the database
    conversation = session.query(Conversation).filter_by(id_conversation=conv_id).first()

    # Only allow deletion if the conversation belongs to the user
    if conversation and conversation.id_account == request.user_id:
        session.delete(conversation)
        session.commit()
        return jsonify({"message": "Conversation suppressed"}), 200

    # Return error if conversation not found or unauthorized
    return jsonify({"error": "Conversation not found or access refused"}), 404


@app.route("/suppressacc", methods=["DELETE"])
@token_required
def suppressacc():
    """
    Deletes an authenticated user's account.
    """
    user_id = request.user_id
    # Fetch the user's account
    account = session.query(Account).filter_by(id_account=user_id).first()
    if account:
        session.delete(account)
        session.commit()
        return jsonify({"message": "Account suppressed"}), 200

    # Return error if account not found
    return jsonify({"error": "Account not found or access refused"}), 404


@app.route("/getuserinfos", methods=["GET"])
@token_required
def getinfos():
    """
    Retrieves information about an authenticated user.
    """
    # Fetch the user's account
    account = session.query(Account).filter_by(id_account=request.user_id).first()
    if account:
        # Convert user's preferred genres into a dict of id -> name
        genres = {e.id_genre: e.name for e in account.genres}
        # Return user profile details as JSON
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
        # User not found in database
        return jsonify({"error": "User not found"}), 404


@app.route("/addgenre", methods=["POST"])
@token_required
def addgenre():
    """
    Adds a genre for an authenticated user.
    """
    user_id = request.user_id
    genre_name = request.json.get("genre")
    # Fetch user account
    account = session.query(Account).filter_by(id_account=user_id).first()
    if not account:
        return jsonify({"error": "User not found"}), 404

    # List all existing genres (for debugging)
    all_genres = session.query(Genre.name).all()
    # Find the requested genre by name
    genre = session.query(Genre).filter_by(name=genre_name).first()
    if not genre:
        return jsonify({"error": "Genre not found"}), 404

    # Associate genre with user if not already linked
    if genre not in account.genres:
        account.genres.append(genre)
        session.commit()
        return (
            jsonify({"message": "Genre added successfully", "id": genre.id_genre}),
            201,
        )
    else:
        # Inform client that genre was already associated
        return jsonify({"message": "Genre already associated with user"}), 200


@app.route("/suppressgenre", methods=["DELETE"])
@token_required
def suppressgenre():
    """
    Deletes a genre for an authenticated user.
    """
    user_id = request.user_id
    genre_id = request.json.get("id")
    # Fetch user account and genre record
    account = session.query(Account).filter_by(id_account=user_id).first()
    genre = session.query(Genre).filter_by(id_genre=genre_id).first()

    # Validate user and genre existence
    if not account or not genre:
        return jsonify({"error": "User not found"}), 404
    # Remove association if present
    if genre in account.genres:
        account.genres.remove(genre)
        session.commit()
        return jsonify({"message": "Genre removed from user"}), 200
    else:
        # Cannot remove a genre not linked to user
        return jsonify({"error": "Genre not associated with user"}), 404

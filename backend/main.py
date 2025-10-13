from flask import request, jsonify
from config import app, db
from models import Contact, User
import jwt
import datetime
from functools import wraps
import logging
import os
import re

# Set up logging to console and file
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/app.log')
    ]
)


# Concise helper function for consistent logging
def log_event(level, message, username=None):
    msg = f"{message} for user '{username}'" if username else message
    getattr(logging, level)(msg)


# Password validation function
def validate_password(password):
    if len(password) < 8:
        return "Password must be at least 8 characters long"
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter"
    if not re.search(r"[0-9]", password):
        return "Password must contain at least one number"
    if not re.search(r"[!@#$%^&.*]", password):
        return "Password must contain at least one special character (!@#$%^&.*)"
    return None


# JWT decorator to protect routes
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].replace("Bearer ", "")
        if not token:
            log_event('warning', "Request failed: Missing Authorization token")
            return jsonify({"message": "Token is missing"}), 401
        try:
            data = jwt.decode(token, app.config["JWT_SECRET_KEY"], algorithms=["HS256"])
            current_user = User.query.filter_by(id=data["user_id"]).first()
            if not current_user:
                log_event('warning', f"Request failed: User ID {data['user_id']} not found")
                return jsonify({"message": "User not found"}), 401
            log_event('debug', "Token validated successfully", current_user.username)
        except jwt.ExpiredSignatureError:
            log_event('warning', "Request failed: Token has expired")
            return jsonify({"message": "Token has expired"}), 401
        except jwt.InvalidTokenError as e:
            log_event('warning', f"Request failed: Invalid token - {str(e)}")
            return jsonify({"message": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated


@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.json
        username = data.get("username")
        password = data.get("password")
        if not username or not password:
            log_event('warning', "Registration failed: Missing username or password", username)
            return jsonify({"message": "Username and password are required"}), 400
        password_error = validate_password(password)
        if password_error:
            log_event('warning', f"Registration failed: {password_error}", username)
            return jsonify({"message": password_error}), 400
        if User.query.filter_by(username=username).first():
            log_event('warning', "Registration failed: Username already exists", username)
            return jsonify({"message": "Username already exists"}), 400
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        log_event('info', "User registered successfully", username)
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        log_event('error', f"Registration server error: {str(e)}", username)
        return jsonify({"message": f"Server error: {str(e)}"}), 500


@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.json
        username = data.get("username")
        password = data.get("password")
        if not username or not password:
            log_event('warning', "Login failed: Missing username or password", username)
            return jsonify({"message": "Username and password are required"}), 400
        user = User.query.filter_by(username=username).first()
        if not user:
            log_event('error', "Login failed: User does not exist", username)
            return jsonify({"message": "Invalid credentials"}), 401
        if not user.check_password(password):
            log_event('warning', "Login failed: Invalid password", username)
            return jsonify({"message": "Invalid credentials"}), 401
        token = jwt.encode(
            {
                "user_id": user.id,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            },
            app.config["JWT_SECRET_KEY"],
            algorithm="HS256"
        )
        log_event('info', "User logged in successfully", username)
        return jsonify({"token": token, "message": "Logged in successfully"}), 200
    except Exception as e:
        log_event('error', f"Login server error: {str(e)}", username)
        return jsonify({"message": f"Server error: {str(e)}"}), 500


@app.route("/logout", methods=["POST"])
def logout():
    log_event('info', "User logged out successfully")
    return jsonify({"message": "Logged out successfully"}), 200


@app.route("/contacts", methods=["GET"])
@token_required
def get_contacts():
    try:
        contacts = Contact.query.all()
        json_contacts = list(map(lambda x: x.to_json(), contacts))
        log_event('info', f"Fetched {len(json_contacts)} contacts successfully")
        return jsonify({"contacts": json_contacts}), 200
    except Exception as e:
        log_event('error', f"Get contacts error: {str(e)}")
        return jsonify({"message": f"Server error: {str(e)}"}), 500


@app.route("/create_contact", methods=["POST"])
@token_required
def create_contact():
    try:
        first_name = request.json.get("firstName")
        last_name = request.json.get("lastName")
        email = request.json.get("email")
        if not first_name or not last_name or not email:
            log_event('warning', "Create contact failed: Missing first name, last name, or email")
            return jsonify({"message": "You must include a first name, last name and email"}), 400
        new_contact = Contact(first_name=first_name, last_name=last_name, email=email)
        db.session.add(new_contact)
        db.session.commit()
        log_event('info', f"Contact created successfully: {first_name} {last_name}, email: {email}")
        return jsonify({"message": "Contact created!"}), 201
    except Exception as e:
        log_event('error', f"Create contact error: {str(e)}")
        return jsonify({"message": f"Server error: {str(e)}"}), 500


@app.route("/update_contact/<int:user_id>", methods=["PATCH"])
@token_required
def update_contact(user_id):
    try:
        contact = Contact.query.get(user_id)
        if not contact:
            log_event('warning', f"Update contact failed: Contact ID {user_id} not found")
            return jsonify({"message": "Contact not found"}), 404
        data = request.json
        contact.first_name = data.get("firstName", contact.first_name)
        contact.last_name = data.get("lastName", contact.last_name)
        contact.email = data.get("email", contact.email)
        db.session.commit()
        log_event('info', f"Contact updated successfully: ID {user_id}")
        return jsonify({"message": "Contact updated."}), 200
    except Exception as e:
        log_event('error', f"Update contact error for ID {user_id}: {str(e)}")
        return jsonify({"message": f"Server error: {str(e)}"}), 500


@app.route("/delete_contact/<int:user_id>", methods=["DELETE"])
@token_required
def delete_contact(user_id):
    try:
        contact = Contact.query.get(user_id)
        if not contact:
            log_event('warning', f"Delete contact failed: Contact ID {user_id} not found")
            return jsonify({"message": "Contact not found"}), 404
        db.session.delete(contact)
        db.session.commit()
        log_event('info', f"Contact deleted successfully: ID {user_id}")
        return jsonify({"message": "Contact deleted!"}), 200
    except Exception as e:
        log_event('error', f"Delete contact error for ID {user_id}: {str(e)}")
        return jsonify({"message": f"Server error: {str(e)}"}), 500


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
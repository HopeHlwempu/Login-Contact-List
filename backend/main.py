from flask import request, jsonify
from config import app, db
from models import Contact, User
import jwt
import datetime
from functools import wraps
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# JWT decorator to protect routes
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].replace("Bearer ", "")
        if not token:
            return jsonify({"message": "Token is missing"}), 401
        try:
            data = jwt.decode(token, app.config["JWT_SECRET_KEY"], algorithms=["HS256"])
            current_user = User.query.filter_by(id=data["user_id"]).first()
            if not current_user:
                return jsonify({"message": "User not found"}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired"}), 401
        except jwt.InvalidTokenError:
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
            return jsonify({"message": "Username and password are required"}), 400
        if User.query.filter_by(username=username).first():
            return jsonify({"message": "Username already exists"}), 400
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        app.logger.debug(f"User {username} registered successfully")
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        app.logger.error(f"Register error: {str(e)}")
        return jsonify({"message": f"Server error: {str(e)}"}), 500

@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.json
        username = data.get("username")
        password = data.get("password")
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            token = jwt.encode(
                {
                    "user_id": user.id,
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
                },
                app.config["JWT_SECRET_KEY"],
                algorithm="HS256"
            )
            app.logger.debug(f"User {username} logged in, token issued")
            return jsonify({"token": token, "message": "Logged in successfully"}), 200
        return jsonify({"message": "Invalid credentials"}), 401
    except Exception as e:
        app.logger.error(f"Login error: {str(e)}")
        return jsonify({"message": f"Server error: {str(e)}"}), 500

@app.route("/logout", methods=["POST"])
def logout():
    # JWT is stateless; logout is handled client-side by removing token
    return jsonify({"message": "Logged out successfully"}), 200

@app.route("/contacts", methods=["GET"])
@token_required
def get_contacts():
    try:
        contacts = Contact.query.all()
        json_contacts = list(map(lambda x: x.to_json(), contacts))
        return jsonify({"contacts": json_contacts}), 200
    except Exception as e:
        app.logger.error(f"Get contacts error: {str(e)}")
        return jsonify({"message": f"Server error: {str(e)}"}), 500

@app.route("/create_contact", methods=["POST"])
@token_required
def create_contact():
    try:
        first_name = request.json.get("firstName")
        last_name = request.json.get("lastName")
        email = request.json.get("email")
        if not first_name or not last_name or not email:
            return jsonify({"message": "You must include a first name, last name and email"}), 400
        new_contact = Contact(first_name=first_name, last_name=last_name, email=email)
        db.session.add(new_contact)
        db.session.commit()
        return jsonify({"message": "User created!"}), 201
    except Exception as e:
        app.logger.error(f"Create contact error: {str(e)}")
        return jsonify({"message": f"Server error: {str(e)}"}), 500

@app.route("/update_contact/<int:user_id>", methods=["PATCH"])
@token_required
def update_contact(user_id):
    try:
        contact = Contact.query.get(user_id)
        if not contact:
            return jsonify({"message": "User not found"}), 404
        data = request.json
        contact.first_name = data.get("firstName", contact.first_name)
        contact.last_name = data.get("lastName", contact.last_name)
        contact.email = data.get("email", contact.email)
        db.session.commit()
        return jsonify({"message": "User updated."}), 200
    except Exception as e:
        app.logger.error(f"Update contact error: {str(e)}")
        return jsonify({"message": f"Server error: {str(e)}"}), 500

@app.route("/delete_contact/<int:user_id>", methods=["DELETE"])
@token_required
def delete_contact(user_id):
    try:
        contact = Contact.query.get(user_id)
        if not contact:
            return jsonify({"message": "User not found"}), 404
        db.session.delete(contact)
        db.session.commit()
        return jsonify({"message": "User deleted!"}), 200
    except Exception as e:
        app.logger.error(f"Delete contact error: {str(e)}")
        return jsonify({"message": f"Server error: {str(e)}"}), 500

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
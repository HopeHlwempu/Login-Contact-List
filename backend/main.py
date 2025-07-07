from flask import request, jsonify
from config import app, db
from models import Contact, User
from flask_login import LoginManager, login_user, login_required, logout_user
import logging

# Set up logging to debug server errors
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception as e:
        app.logger.error(f"Error loading user: {str(e)}")
        return None

@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.json
        username = data.get("username")
        password = data.get("password")
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return jsonify({"message": "Logged in successfully"}), 200
        return jsonify({"message": "Invalid credentials"}), 401
    except Exception as e:
        app.logger.error(f"Login error: {str(e)}")
        return jsonify({"message": f"Server error: {str(e)}"}), 500

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    try:
        logout_user()
        return jsonify({"message": "Logged out successfully"}), 200
    except Exception as e:
        app.logger.error(f"Logout error: {str(e)}")
        return jsonify({"message": f"Server error: {str(e)}"}), 500

@app.route("/contacts", methods=["GET"])
@login_required
def get_contacts():
    try:
        contacts = Contact.query.all()
        json_contacts = list(map(lambda x: x.to_json(), contacts))
        return jsonify({"contacts": json_contacts}), 200
    except Exception as e:
        app.logger.error(f"Get contacts error: {str(e)}")
        return jsonify({"message": f"Server error: {str(e)}"}), 500

@app.route("/create_contact", methods=["POST"])
@login_required
def create_contact():
    try:
        first_name = request.json.get("firstName")
        last_name = request.json.get("lastName")
        email = request.json.get("email")

        if not first_name or not last_name or not email:
            return (
                jsonify({"message": "You must include a first name, last name and email"}),
                400,
            )

        new_contact = Contact(first_name=first_name, last_name=last_name, email=email)
        db.session.add(new_contact)
        db.session.commit()
        return jsonify({"message": "User created!"}), 201
    except Exception as e:
        app.logger.error(f"Create contact error: {str(e)}")
        return jsonify({"message": f"Server error: {str(e)}"}), 500

@app.route("/update_contact/<int:user_id>", methods=["PATCH"])
@login_required
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
@login_required
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
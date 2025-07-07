from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)

# Configure CORS to allow requests from the frontend origin
CORS(app, resources={r"/*": {"origins": "http://localhost:5173", "supports_credentials": True}})

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydatabase.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "your-secret-key"  # Required for session management

db = SQLAlchemy(app)
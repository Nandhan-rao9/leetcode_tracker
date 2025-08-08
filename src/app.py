# src/app.py
from flask import Flask, jsonify
from flask_cors import CORS
from .db import create_indexes
from .routes.import_routes import bp as import_bp
from .routes.problems_routes import problems_bp   # 👈 change this
from .routes.notes_tags_routes import notes_tags_bp  # make sure this matches too

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173","http://localhost:3000","http://127.0.0.1:5173","https://leetcode.com"]}})

app.register_blueprint(import_bp, url_prefix="/")
app.register_blueprint(problems_bp, url_prefix="/")     # 👈 keep problems_bp here
app.register_blueprint(notes_tags_bp, url_prefix="/")   # 👈 notes_tags_bp here

create_indexes()

@app.get("/health")
def health():
    return jsonify(status="ok"), 200

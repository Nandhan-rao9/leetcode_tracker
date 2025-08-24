# src/app.py
from flask import Flask, jsonify
from flask_cors import CORS
from .db import create_indexes
from .routes.import_routes import bp as import_bp
from .routes.problems_routes import bp_problems
from .routes.notes_tags_routes import bp_notes_tags
from .routes.export_routes import bp_export
from .routes.read_routes import bp_read  # ← add

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000"]}})

app.register_blueprint(import_bp, url_prefix="/")
app.register_blueprint(bp_problems, url_prefix="/")
app.register_blueprint(bp_notes_tags, url_prefix="/")
app.register_blueprint(bp_export, url_prefix="/")
app.register_blueprint(bp_read, url_prefix="/")  # ← add

create_indexes()

@app.get("/health")
def health():
    return jsonify(status="ok"), 200

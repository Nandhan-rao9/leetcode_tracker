# src/app.py
from flask import Flask, jsonify
from .db import create_indexes
from .routes.import_routes import bp as import_bp
from .routes.problems_routes import bp_problems
from .routes.notes_tags_routes import bp_notes_tags
from .routes.export_routes import bp_export


app = Flask(__name__)

app.register_blueprint(import_bp, url_prefix="/")
app.register_blueprint(bp_problems, url_prefix="/")
app.register_blueprint(bp_notes_tags, url_prefix="/")  # if present
app.register_blueprint(bp_export, url_prefix="/")


create_indexes()

@app.get("/health")
def health():
    return jsonify(status="ok"), 200

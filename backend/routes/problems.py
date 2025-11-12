# backend/routes/problems.py
from flask import Blueprint, jsonify, request
from utils.db import unsolved_col, solved_col

problems_bp = Blueprint("problems", __name__)

@problems_bp.route("/api/problems/search", methods=["GET"])
def search_problems():
    topic = request.args.get("topic")
    difficulty = request.args.get("difficulty")
    query = {}

    if topic:
        query["all_topics"] = {"$in": [topic.lower()]}
    if difficulty:
        # unify capitalization
        query["difficulty"] = difficulty.capitalize()

    fields = {"_id": 0, "title": 1, "difficulty": 1, "link": 1, "all_topics": 1}
    results = list(unsolved_col.find(query, fields))
    # if none found, search solved collection as well
    if not results:
        results = list(solved_col.find(query, fields))
    return jsonify(results)

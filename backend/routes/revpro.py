# backend/routes/revpro.py
from flask import Blueprint, jsonify, request
from utils.db import solved_col, unsolved_col

problems_bp = Blueprint("problems", __name__, url_prefix="/api/problems")


# ---------------------------------------------------------
# Helper: parse common query params safely
# ---------------------------------------------------------
def parse_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


# ---------------------------------------------------------
# GET /api/problems
# Unified, powerful problems explorer
# ---------------------------------------------------------
@problems_bp.route("", methods=["GET"])
def list_problems():
    """
    Query params:
    - solved=true|false
    - topic=graphs
    - difficulty=Easy|Medium|Hard
    - min_ac=0..100
    - max_ac=0..100
    - sort=acRate|num_occur|title
    - order=asc|desc
    - page=1
    - limit=50
    """

    # ---------- Source selection ----------
    solved = request.args.get("solved", "true").lower() == "true"
    col = solved_col if solved else unsolved_col

    # ---------- Filters ----------
    query = {}

    topic = request.args.get("topic")
    if topic:
        query["all_topics"] = {"$in": [topic]}

    difficulty = request.args.get("difficulty")
    if difficulty:
        query["difficulty"] = difficulty.capitalize()

    min_ac = parse_int(request.args.get("min_ac"), 0)
    max_ac = parse_int(request.args.get("max_ac"), 100)
    if min_ac > 0 or max_ac < 100:
        query["acRate"] = {"$gte": min_ac, "$lte": max_ac}

    # ---------- Sorting ----------
    sort_field = request.args.get("sort", "title")
    order = -1 if request.args.get("order") == "desc" else 1

    allowed_sort_fields = {"title", "acRate", "num_occur", "difficulty"}
    if sort_field not in allowed_sort_fields:
        sort_field = "title"

    # ---------- Pagination ----------
    page = max(parse_int(request.args.get("page"), 1), 1)
    limit = min(parse_int(request.args.get("limit"), 50), 100)
    skip = (page - 1) * limit

    # ---------- Projection ----------
    projection = {
        "_id": 0,
        "title": 1,
        "difficulty": 1,
        "all_topics": 1,
        "companies": 1,
        "link": 1,
        "num_occur": 1,
        "acRate": 1,
    }

    # ---------- Query execution ----------
    cursor = (
        col.find(query, projection)
        .sort(sort_field, order)
        .skip(skip)
        .limit(limit)
    )

    problems = list(cursor)
    total = col.count_documents(query)

    # ---------- Response ----------
    return jsonify({
        "meta": {
            "page": page,
            "limit": limit,
            "total": total,
            "returned": len(problems),
            "solved": solved
        },
        "filters": {
            "topic": topic,
            "difficulty": difficulty,
            "min_ac": min_ac,
            "max_ac": max_ac
        },
        "data": problems
    })

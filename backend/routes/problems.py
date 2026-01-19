# backend/routes/problems.py
from flask import Blueprint, jsonify, request
from utils.db import problems_master, user_solved_col

problems_bp = Blueprint("problems", __name__)

# ---------- SEARCH ----------
@problems_bp.route("/api/problems/search", methods=["GET"])
def search():
    topic = request.args.get("topic")
    difficulty = request.args.get("difficulty")
    username = request.args.get("user")

    solved = set()
    if username:
        solved = {
            d["slug"]
            for d in user_solved_col(username).find({}, {"_id": 0, "slug": 1})
        }

    query = {}
    if topic:
        query["topics"] = topic.lower()
    if difficulty:
        query["difficulty"] = difficulty.capitalize()

    projection = {
        "_id": 0,
        "id": 1,
        "title": 1,
        "difficulty": 1,
        "topics": 1
    }

    results = []
    for p in problems_master.find(query, projection):
        p["is_solved"] = p["id"] in solved
        p["link"] = f"https://leetcode.com/problems/{p['id']}/"
        results.append(p)

    return jsonify(results)


# ---------- REVIEW ----------
@problems_bp.route("/api/review/today", methods=["GET"])
def review_today():
    username = request.args.get("user")
    if not username:
        return jsonify([])

    solved = list(
        user_solved_col(username)
        .find({}, {"_id": 0, "slug": 1, "title": 1})
        .sort("archived_at", -1)
        .limit(15)
    )

    if not solved:
        return jsonify([])

    slugs = [s["slug"] for s in solved]

    master_docs = {
        p["_id"]: p
        for p in problems_master.find(
            {"_id": {"$in": slugs}},
            {
                "_id": 1,
                "title": 1,
                "difficulty": 1,
                "acRate": 1,
                "topics": 1,
                "paidOnly": 1,
                "hasSolution": 1,
                "hasVideoSolution": 1,
            }
        )
    }

    results = []
    for s in solved:
        slug = s["slug"]
        m = master_docs.get(slug)

        results.append({
            "slug": slug,
            "title": m["title"] if m else s.get("title", slug),
            "difficulty": m["difficulty"] if m else "—",
            "acRate": m.get("acRate") if m else None,
            "topics": m.get("topics", []) if m else [],
            "paidOnly": m.get("paidOnly", False) if m else False,
            "hasSolution": m.get("hasSolution", False) if m else False,
            "hasVideoSolution": m.get("hasVideoSolution", False) if m else False,
            "link": f"https://leetcode.com/problems/{slug}/",
            "indexed": bool(m),
        })

    return jsonify(results)
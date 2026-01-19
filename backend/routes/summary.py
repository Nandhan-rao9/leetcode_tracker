# backend/routes/summary.py
from flask import Blueprint, jsonify, request
from utils.db import problems_master, user_solved_col

summary_bp = Blueprint("summary", __name__)

@summary_bp.route("/api/summary", methods=["GET"])
def summary():
    username = request.args.get("user")
    if not username:
        return jsonify({"error": "user required"}), 400

    total_problems = problems_master.count_documents({})
    total_solved = user_solved_col(username).count_documents({})

    companies = problems_master.distinct("companies")

    return jsonify({
        "totalSolved": total_solved,
        "totalProblems": total_problems,
        "companies": len(companies)
    })

@summary_bp.route("/api/insights", methods=["GET"])
def insights():
    from collections import Counter

    counter = Counter()

    cursor = problems_master.find({}, {"_id": 0, "topics": 1})

    for doc in cursor:
        topics = doc.get("topics", [])
        if isinstance(topics, list):
            for t in topics:
                counter[t] += 1

    if not counter:
        return jsonify({
            "most_requested_topic": "N/A",
            "weakest_topic": "N/A",
            "daily_review_count": 0,
            "next_review": "—"
        })

    most_common = counter.most_common(1)[0][0]

    return jsonify({
        "most_requested_topic": most_common,
        "weakest_topic": "Dynamic Programming",
        "daily_review_count": 3,
        "next_review": "12h"
    })
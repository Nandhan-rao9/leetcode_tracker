# backend/routes/summary.py
from flask import Blueprint, jsonify
from utils.db import solved_col, unsolved_col

summary_bp = Blueprint("summary", __name__)

@summary_bp.route("/api/summary", methods=["GET"])
def get_summary():
    total_solved = solved_col.count_documents({})
    total_unsolved = unsolved_col.count_documents({})
    total_problems = total_solved + total_unsolved

    # aggregate company set from solved_col and unsolved_col
    companies = set()
    for doc in solved_col.find({}, {"companies": 1}):
        companies.update(doc.get("companies", []) or [])
    for doc in unsolved_col.find({}, {"companies": 1}):
        companies.update(doc.get("companies", []) or [])

    return jsonify({
        "totalSolved": total_solved,
        "totalProblems": total_problems,
        "companies": len(companies)
    })
@summary_bp.route("/api/insights", methods=["GET"])
def get_insights():
    """
    Return quick insights about problem distribution.
    """
    pipeline = [
        {"$unwind": "$all_topics"},
        {"$group": {"_id": "$all_topics", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 3},
    ]
    top_topics = list(solved_col.aggregate(pipeline))
    most_requested = top_topics[0]["_id"] if top_topics else "N/A"
    
    # Example static placeholders for now
    insights = {
        "most_requested_topic": most_requested,
        "weakest_topic": "Dynamic Programming",
        "daily_review_count": 3,
        "next_review": "12h",
    }
    return jsonify(insights)


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

# backend/routes/companies.py
from flask import Blueprint, jsonify
from utils.db import solved_col, unsolved_col
from urllib.parse import unquote

companies_bp = Blueprint("companies", __name__)

@companies_bp.route("/api/companies/top", methods=["GET"])
def top_companies():
    pipeline = [
        {"$unwind": "$companies"},
        {"$group": {"_id": "$companies", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 20}
    ]
    results = list(solved_col.aggregate(pipeline))
    total = sum(r["count"] for r in results) or 1

    data = [
        {
            "name": r["_id"],
            "count": r["count"],
            "ready": round(r["count"] / total, 2)
        }
        for r in results if r["_id"]
    ]
    return jsonify(data)

@companies_bp.route("/api/companies/<company>", methods=["GET"])
def company_problems(company):
    # decode in case frontend urlencoded the company name
    company_decoded = unquote(company)
    query = {"companies": {"$in": [company_decoded]}}
    fields = {"_id": 0, "title": 1, "difficulty": 1, "all_topics": 1, "num_occur": 1, "link": 1}
    # prefer unsolved collection (company problem bank), but fall back to solved if empty
    problems = list(unsolved_col.find(query, fields))
    if not problems:
        problems = list(solved_col.find(query, fields))
    return jsonify({"problems": problems})

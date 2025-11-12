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
@companies_bp.route("/api/companies/compare", methods=["POST"])
def compare_companies():
    """
    Compare topic distributions between companies.
    """
    data = request.get_json(force=True)
    company_list = data.get("companies", [])
    comparison = {}

    for company in company_list:
        pipeline = [
            {"$match": {"companies": {"$in": [company]}}},
            {"$unwind": "$all_topics"},
            {"$group": {"_id": "$all_topics", "count": {"$sum": 1}}},
            {"$sort": {"count": 1}},  # ascending
        ]
        results = list(unsolved_col.aggregate(pipeline))
        comparison[company] = {r["_id"]: r["count"] for r in results}

    return jsonify(comparison)
@companies_bp.route("/api/companies/<company>/plan", methods=["POST"])
def generate_plan(company):
    data = request.get_json(force=True)
    num = int(data.get("num", 10))
    include_solved = data.get("include_solved", False)
    query = {"companies": {"$in": [company]}}
    col = unsolved_col if not include_solved else solved_col

    problems = list(col.find(query, {"_id": 0, "title": 1, "difficulty": 1, "all_topics": 1}))
    # ensure diversity — pick evenly by topic
    by_topic = {}
    for p in problems:
        for t in p.get("all_topics", []):
            by_topic.setdefault(t, []).append(p)
    final = []
    topics = sorted(by_topic.keys())
    i = 0
    while len(final) < num and topics:
        t = topics[i % len(topics)]
        if by_topic[t]:
            final.append(by_topic[t].pop(0))
        i += 1
    return jsonify(final)
@companies_bp.route("/api/companies/<company>/plan", methods=["POST"])
def generate_plan(company):
    """
    Generate a diverse problem plan for a company.
    """
    from random import shuffle

    data = request.get_json(force=True)
    num = int(data.get("num", 10))
    include_solved = data.get("include_solved", False)

    query = {"companies": {"$in": [company]}}
    col = unsolved_col if not include_solved else solved_col

    problems = list(col.find(query, {"_id": 0, "title": 1, "difficulty": 1, "all_topics": 1, "link": 1}))

    if not problems:
        return jsonify({"error": "No problems found for this company"}), 404

    # Group by topic to ensure diversity
    by_topic = {}
    for p in problems:
        for t in p.get("all_topics", []):
            by_topic.setdefault(t, []).append(p)

    # Randomized balanced selection
    topics = list(by_topic.keys())
    shuffle(topics)
    plan = []
    i = 0
    while len(plan) < num and any(by_topic.values()):
        topic = topics[i % len(topics)]
        if by_topic[topic]:
            plan.append(by_topic[topic].pop(0))
        i += 1

    return jsonify(plan[:num])

# backend/routes/companies.py
from flask import Blueprint, jsonify, request
from utils.db import problems_master, user_solved_col
from urllib.parse import unquote
import random

companies_bp = Blueprint("companies", __name__)

# ---------- TOP COMPANIES ----------
def readiness_bucket(raw_score: float) -> int:
    """
    raw_score = weighted_solved / weighted_total
    Returns a motivating but realistic readiness percentage
    """

    if raw_score >= 0.85:
        return 92
    if raw_score >= 0.70:
        return 80
    if raw_score >= 0.55:
        return 68
    if raw_score >= 0.40:
        return 55
    if raw_score >= 0.25:
        return 42
    if raw_score >= 0.15:
        return 30
    if raw_score > 0:
        return 22
    return 15



@companies_bp.route("/api/companies/top", methods=["GET"])
def top_companies():
    username = request.args.get("user")

    solved = set()
    if username:
        solved = {
            d["slug"]
            for d in user_solved_col(username).find({}, {"_id": 0, "slug": 1})
        }

    company_stats = {}

    cursor = problems_master.find(
        {},
        {"_id": 1, "companies": 1, "num_occur": 1}
    )

    for p in cursor:
        slug = p["_id"]
        freq = min(p.get("num_occur", 1),15)

        companies = p.get("companies")
        if not isinstance(companies, list):
            continue

        for company in companies:
            if company not in company_stats:
                company_stats[company] = {
                    "total_problems": 0,
                    "weighted_total": 0,
                    "weighted_solved": 0,
                }

            company_stats[company]["total_problems"] += 1
            company_stats[company]["weighted_total"] += freq

            if slug in solved:
                company_stats[company]["weighted_solved"] += freq

    result = []
    for company, s in company_stats.items():
        if s["weighted_total"] == 0:
            continue

        raw_score = s["weighted_solved"] / s["weighted_total"]
        readiness = readiness_bucket(raw_score)

        result.append({
            "name": company,
            "commonProblems": s["total_problems"],
            "readiness": readiness,
        })

    result.sort(
        key=lambda x: (x["readiness"], x["commonProblems"]),
        reverse=True
    )

    return jsonify(result[:8])

# ---------- COMPANY PROBLEMS ----------
@companies_bp.route("/api/companies/<company>", methods=["GET"])
def company_problems(company):
    company = unquote(company)
    username = request.args.get("user")

    # 1. Load solved slugs for the user
    solved = set()
    if username:
        solved = {
            d["slug"]
            for d in user_solved_col(username).find(
                {}, {"_id": 0, "slug": 1}
            )
        }

    # 2. Query problems_master
    query = {
        "companies": company
    }

    projection = {
        "_id": 1,          # 🔥 slug is stored here
        "title": 1,
        "difficulty": 1,
        "topics": 1,
        "num_occur": 1,
    }

    problems = []

    for p in problems_master.find(query, projection):
        slug = p["_id"]

        problems.append({
            "slug": slug,
            "title": p["title"],
            "difficulty": p["difficulty"],
            "topics": p.get("topics", []),
            "num_occur": p.get("num_occur", 0),
            "is_solved": slug in solved,
            "link": f"https://leetcode.com/problems/{slug}/",
        })

    return jsonify({"problems": problems})



# ---------- SMART PLAN ----------
@companies_bp.route("/api/companies/<company>/smart_plan", methods=["POST"])
def smart_plan(company):
    company = unquote(company)
    data = request.get_json(force=True)

    username = data.get("user")
    num = int(data.get("num", 10))
    include_solved = data.get("include_solved", False)
    difficulties = data.get("difficulties", ["Easy", "Medium", "Hard"])

    # 1. Load solved slugs
    solved = set()
    if username:
        solved = {
            d["slug"]
            for d in user_solved_col(username).find(
                {}, {"_id": 0, "slug": 1}
            )
        }

    # 2. Query problems_master
    query = {
        "companies": company,
        "difficulty": {"$in": difficulties},
    }

    projection = {
        "_id": 1,          # 🔥 slug lives here
        "title": 1,
        "difficulty": 1,
        "topics": 1,
        "acRate": 1,
        "num_occur": 1,
    }

    problems = list(problems_master.find(query, projection))
    random.shuffle(problems)

    final = []
    for p in problems:
        slug = p["_id"]  # ✅ CORRECT SLUG

        if not include_solved and slug in solved:
            continue

        final.append({
            "slug": slug,
            "title": p["title"],
            "difficulty": p["difficulty"],
            "acRate": p.get("acRate", None),
            "topics": p.get("topics", []),
            "is_solved": slug in solved,
            "link": f"https://leetcode.com/problems/{slug}/",
        })

        if len(final) == num:
            break

    return jsonify(final)

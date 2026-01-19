# backend/routes/companies.py
from flask import Blueprint, jsonify, request
from utils.db import problems_master, user_solved_col
from urllib.parse import unquote
import random

companies_bp = Blueprint("companies", __name__)

# ---------- TOP COMPANIES ----------
@companies_bp.route("/api/companies/top", methods=["GET"])
def top_companies():
    from collections import defaultdict

    counter = defaultdict(int)

    cursor = problems_master.find({}, {"_id": 0, "by_company": 1})

    for doc in cursor:
        by_company = doc.get("by_company", {})

        if not isinstance(by_company, dict):
            continue

        for company, raw_count in by_company.items():
            # Normalize count
            if isinstance(raw_count, dict):
                raw_count = raw_count.get("count", 0)

            if isinstance(raw_count, int):
                counter[company] += raw_count

    sorted_companies = sorted(
        counter.items(),
        key=lambda x: x[1],
        reverse=True
    )[:20]

    total = sum(c for _, c in sorted_companies) or 1

    return jsonify([
        {
            "name": company,
            "count": count,
            "ready": round(count / total, 2)
        }
        for company, count in sorted_companies
    ])



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
            "topics": p.get("topics", []),
            "is_solved": slug in solved,
            "link": f"https://leetcode.com/problems/{slug}/",
        })

        if len(final) == num:
            break

    return jsonify(final)

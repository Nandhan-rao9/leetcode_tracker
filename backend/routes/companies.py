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

def extract_slug(doc):
    # Preferred
    if isinstance(doc.get("slug"), str):
        return doc["slug"]

    # Legacy LeetCode ingestion
    if isinstance(doc.get("titleSlug"), str):
        return doc["titleSlug"]

    # When slug was used as _id
    if isinstance(doc.get("_id"), str):
        return doc["_id"]

    # Fallback from link
    link = doc.get("link")
    if isinstance(link, str) and "/problems/" in link:
        return link.split("/problems/")[1].strip("/")

    return None



# backend/routes/companies.py

@companies_bp.route("/api/companies/top", methods=["GET"])
def top_companies():
    username = request.args.get("user")

    # 1. Load solved slugs SAFELY
    solved = set()
    if username:
        # Use the same logic as smart_plan to get solved slugs
        for d in user_solved_col(username).find({}, {"_id": 0, "slug": 1}):
            if "slug" in d:
                solved.add(d["slug"])

    TARGET = 120
    company_map = {}

    # 2. Query master problems
    cursor = problems_master.find(
        {},
        {"_id": 1, "slug": 1, "companies": 1, "num_occur": 1}
    )

    for p in cursor:
        # Consistency: smart_plan uses _id as the slug
        slug = p.get("_id") 
        if not slug:
            continue

        freq = p.get("num_occur", 1)
        companies = p.get("companies", [])

        for c in companies:
            company_map.setdefault(c, []).append({
                "slug": slug,
                "freq": freq
            })

    result = []

    for company, problems in company_map.items():
        # Sort by frequency and take the top TARGET problems
        problems.sort(key=lambda x: x["freq"], reverse=True)
        top_problems = problems[:TARGET]

        # Calculate how many of these top problems are in the 'solved' set
        solved_count = sum(1 for p in top_problems if p["slug"] in solved)

        # Calculate readiness percentage
        readiness = int((solved_count / TARGET) * 100)
        
        # Apply the floor (15) and cap (92) as per your existing logic
        readiness = max(15, min(readiness, 92))

        result.append({
            "name": company,
            "commonProblems": len(problems),
            "readiness": readiness
        })

    # Sort companies by readiness and problem count
    result.sort(
        key=lambda x: (x["readiness"], x["commonProblems"]),
        reverse=True
    )

    return jsonify(result[:12]) # Increased limit to show more


# ---------- COMPANY PROBLEMS ----------
@companies_bp.route("/api/companies/<company>", methods=["GET"])
def company_problems(company):
    company = unquote(company)
    username = request.args.get("user")

    solved = set()
    if username:
        for d in user_solved_col(username).find({}):
            slug = extract_slug(d)
            if slug:
                solved.add(slug)

    query = {"companies": company}
    projection = {
        "_id": 1,
        "slug": 1,
        "title": 1,
        "difficulty": 1,
        "topics": 1,
        "num_occur": 1,
    }

    problems = []

    for p in problems_master.find(query, projection):
        slug = extract_slug(p)
        if not slug:
            continue

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

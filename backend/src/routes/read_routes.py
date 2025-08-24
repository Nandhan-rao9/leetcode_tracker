# src/routes/read_routes.py
from flask import Blueprint, request, jsonify
from math import ceil
from pymongo import DESCENDING
from ..db import db

bp_read = Blueprint("read", __name__)

# ---------- Submissions (direct read) ----------
@bp_read.get("/submissions")
def list_submissions():
    """
    GET /submissions?userId=<id>&page=1&pageSize=500
    Reads db.submissions directly. Assumes documents carry at least:
      userId, submittedAt (ISO), problemId or slug, plus we try to enrich with db.problems by slug.
    """
    user_id = (request.args.get("userId") or "").strip()
    if not user_id:
        return jsonify(message="userId required"), 400

    page = max(int(request.args.get("page", 1)), 1)
    page_size = min(max(int(request.args.get("pageSize", 50)), 1), 1000)

    q = {"userId": user_id}
    cur = db.submissions.find(q).sort("submittedAt", DESCENDING)

    # count_documents works across PyMongo versions
    total = cur.collection.count_documents(q)

    docs = list(cur.skip((page - 1) * page_size).limit(page_size))
    # Try to enrich with problems if we have slug
    problems_by_slug = {}
    slugs = [d.get("slug") for d in docs if d.get("slug")]
    if slugs:
        for p in db.problems.find({"slug": {"$in": slugs}}, {"_id": 0, "slug": 1, "title": 1, "url": 1, "difficulty": 1, "lcTags": 1}):
            problems_by_slug[p["slug"]] = p

    items = []
    for d in docs:
        item = {
            "userId": d.get("userId"),
            "submittedAt": d.get("submittedAt"),
            "problemId": d.get("problemId"),
            "slug": d.get("slug"),
            "title": d.get("title"),
            "url": d.get("url"),
            "difficulty": d.get("difficulty"),
            "lcTags": d.get("lcTags"),
            "lang": d.get("lang"),
        }
        # fill gaps from problems collection
        if item.get("slug") and problems_by_slug.get(item["slug"]):
            meta = problems_by_slug[item["slug"]]
            item["title"] = item["title"] or meta.get("title")
            item["url"] = item["url"] or meta.get("url")
            item["difficulty"] = item["difficulty"] or meta.get("difficulty")
            item["lcTags"] = item["lcTags"] or meta.get("lcTags")
        items.append(item)

    return jsonify({
        "items": items,
        "total": total,
        "page": page,
        "pages": ceil(total / page_size) if page_size else 1
    })


# ---------- Companies (direct read) ----------
@bp_read.get("/companies")
def list_companies():
    """
    GET /companies
    Returns [{ company, count }] from db.companies_problems.
    Falls back to [] if that collection isn't present.
    """
    if "companies_problems" not in db.list_collection_names():
        return jsonify([])

    pipeline = [
        {"$group": {"_id": "$company", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$project": {"_id": 0, "company": "$_id", "count": 1}},
    ]
    out = list(db.companies_problems.aggregate(pipeline))
    return jsonify(out)


@bp_read.get("/problems/companies/top")
def companies_top():
    """
    GET /problems/companies/top?limit=20
    Uses companies_problems directly.
    """
    limit = min(max(int(request.args.get("limit", 20)), 1), 200)

    if "companies_problems" not in db.list_collection_names():
        return jsonify([])

    pipeline = [
        {"$group": {"_id": "$company", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": limit},
        {"$project": {"_id": 0, "company": "$_id", "count": 1}},
    ]
    out = list(db.companies_problems.aggregate(pipeline))
    return jsonify(out)


# ---------- Problems (filters + optional company) ----------
@bp_read.get("/problems")
def list_problems():
    """
    GET /problems?search=&difficulty=&tag=&company=&page=1&pageSize=20

    - Base: db.problems (has slug/title/url/difficulty/lcTags).
    - If company is provided AND companies_problems exists:
        join companies_problems → problems by URL to filter to that company’s set.
      We assume companies_problems.problem_link == problems.url.
    - If only problems_min exists (no per-company rows), we still return problems
      but company filter yields empty set (graceful).
    """
    search = (request.args.get("search") or "").strip()
    difficulty = (request.args.get("difficulty") or "").strip()
    tag = (request.args.get("tag") or "").strip()
    company = (request.args.get("company") or "").strip()

    page = max(int(request.args.get("page", 1)), 1)
    page_size = min(max(int(request.args.get("pageSize", 20)), 1), 200)

    # If company filter and we have companies_problems, preselect URLs for that company
    urls = None
    if company and "companies_problems" in db.list_collection_names():
        urls = [r["problem_link"] for r in db.companies_problems.find(
            {"company": company}, {"_id": 0, "problem_link": 1}
        )]

        if not urls:
            return jsonify({"items": [], "total": 0, "page": 1, "pages": 1})

    q = {}
    if search:
        q["title"] = {"$regex": search, "$options": "i"}
    if difficulty:
        q["difficulty"] = difficulty
    if tag:
        q["lcTags"] = {"$in": [tag]}
    if urls is not None:
        q["url"] = {"$in": urls}

    cur = db.problems.find(q, {"_id": 0, "slug": 1, "title": 1, "url": 1, "difficulty": 1, "lcTags": 1})
    total = cur.collection.count_documents(q)

    # Optionally attach frequency if you have problems_min
    # (match by url == problem_link)
    freq_by_url = {}
    if "problems_min" in db.list_collection_names():
        for pm in db.problems_min.find({}, {"_id": 0, "problem_link": 1, "num_occur": 1}):
            freq_by_url[pm["problem_link"]] = pm.get("num_occur", 0)

    items = []
    for p in cur.skip((page - 1) * page_size).limit(page_size):
        p["numOccur"] = freq_by_url.get(p.get("url"), None)
        items.append(p)

    return jsonify({
        "items": items,
        "total": total,
        "page": page,
        "pages": ceil(total / page_size) if page_size else 1
    })

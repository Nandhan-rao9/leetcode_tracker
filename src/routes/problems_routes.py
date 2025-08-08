from flask import Blueprint, request, jsonify
from datetime import datetime
from ..db import db

problems_bp = Blueprint("problems", __name__)

def _int_arg(name, default):
    try:
        return int(request.args.get(name, default))
    except Exception:
        return default

@problems_bp.get("/problems")
def list_problems():
    q = (request.args.get("q") or "").strip()
    difficulty = request.args.get("difficulty")
    tags = request.args.get("tags")
    user_id = request.args.get("userId")
    date_from = request.args.get("from")
    date_to = request.args.get("to")
    sort = request.args.get("sort", "title")          # title|difficulty|lastSolved
    order = _int_arg("order", 1)                      # 1|-1
    limit = min(max(_int_arg("limit", 50), 1), 200)
    skip = max(_int_arg("skip", 0), 0)

    match = {}
    if difficulty:
        match["difficulty"] = difficulty
    if q:
        match["title"] = {"$regex": q, "$options": "i"}
    if tags:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        if tag_list:
            match["lcTags"] = {"$all": tag_list}

    pipeline = [{"$match": match}]

    # Join last submission for this user (optional)
    if user_id:
        sub_match = {
            "$expr": {
                "$and": [
                    {"$eq": ["$problemId", "$$pid"]},
                    {"$eq": ["$userId", user_id]},
                ]
            }
        }
        time_cond = {}
        if date_from:
            try: time_cond["$gte"] = datetime.fromisoformat(date_from)
            except: pass
        if date_to:
            try: time_cond["$lte"] = datetime.fromisoformat(date_to)
            except: pass
        if time_cond:
            sub_match = {"$and": [sub_match, {"submittedAt": time_cond}]}

        pipeline += [
            {
                "$lookup": {
                    "from": "submissions",
                    "let": {"pid": "$_id"},
                    "pipeline": [
                        {"$match": sub_match if isinstance(sub_match, dict) else {"$expr": sub_match}},
                        {"$sort": {"submittedAt": -1}},
                        {"$limit": 1},
                        {"$project": {"submittedAt": 1}},
                    ],
                    "as": "lastSub",
                }
            },
            {"$addFields": {"lastSolved": {"$ifNull": [{"$arrayElemAt": ["$lastSub.submittedAt", 0]}, None]}}},
            {"$project": {"lastSub": 0}},
        ]

        # Join user custom tags
        pipeline += [
            {
                "$lookup": {
                    "from": "userProblemTags",
                    "let": {"pid": "$_id"},
                    "pipeline": [
                        {"$match": {"$expr": {"$and": [
                            {"$eq": ["$problemId", "$$pid"]},
                            {"$eq": ["$userId", user_id]}
                        ]}}},
                        {"$project": {"_id": 0, "tag": 1}}
                    ],
                    "as": "customTagsDocs"
                }
            },
            {"$addFields": {"customTags": {"$map": {"input": "$customTagsDocs", "as": "t", "in": "$$t.tag"}}}},
            {"$project": {"customTagsDocs": 0}},
        ]
    else:
        # No user -> empty customTags
        pipeline += [{"$addFields": {"customTags": []}}]

    # Explicit projection to ensure we always return these fields
    pipeline += [{
        "$project": {
            "title": 1,
            "url": 1,
            "difficulty": 1,
            "lcTags": 1,
            "customTags": 1,
            "createdAt": 1,
            "updatedAt": 1,
            "lastSolved": 1
        }
    }]

    # Sorting + pagination
    sort_map = {"title": "title", "difficulty": "difficulty", "lastSolved": "lastSolved"}
    sort_key = sort_map.get(sort, "title")

    pipeline_data = pipeline + [
        {"$sort": {sort_key: order}},
        {"$skip": skip},
        {"$limit": limit},
    ]
    pipeline_count = pipeline + [{"$count": "total"}]

    docs = list(db.problems.aggregate(pipeline_data))
    total_doc = list(db.problems.aggregate(pipeline_count))
    total = total_doc[0]["total"] if total_doc else 0

    # Serialize datetimes to ISO
    def _iso(dt):
        return dt.isoformat() if isinstance(dt, datetime) else dt

    for d in docs:
        d["_id"] = str(d.get("_id"))
        d["createdAt"] = _iso(d.get("createdAt"))
        d["updatedAt"] = _iso(d.get("updatedAt"))
        d["lastSolved"] = _iso(d.get("lastSolved"))

    return jsonify({"items": docs, "total": total, "limit": limit, "skip": skip}), 200

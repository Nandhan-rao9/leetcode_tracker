# src/routes/problems_routes.py
from flask import Blueprint, request, jsonify
from datetime import datetime
from ..db import db

bp_problems = Blueprint("problems", __name__)

@bp_problems.get("/problems")
def list_problems():
    q          = (request.args.get("q") or "").strip()
    difficulty = request.args.get("difficulty")  # "Easy" | "Medium" | "Hard"
    tags       = request.args.get("tags")        # comma-separated lc tags
    user_id    = request.args.get("userId")      # for lastSolved/firstSolved
    sort       = request.args.get("sort", "title")  # "title" | "lastSolved" | "firstSolved" | "difficulty"
    order      = int(request.args.get("order", "1"))  # 1 asc, -1 desc
    limit      = min(int(request.args.get("limit", "20")), 200)
    skip       = max(int(request.args.get("skip", "0")), 0)

    match = {}
    if q:
        match["title"] = {"$regex": q, "$options": "i"}
    if difficulty:
        match["difficulty"] = difficulty
    if tags:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        if tag_list:
            match["lcTags"] = {"$all": tag_list}

    pipeline = [{"$match": match}]

    # Attach first/last solved for this user (if provided)
    if user_id:
        pipeline += [
            {"$lookup": {
                "from": "submissions",
                "let": {"pid": "$_id"},
                "pipeline": [
                    {"$match": {"$expr": {"$and": [
                        {"$eq": ["$problemId", "$$pid"]},
                        {"$eq": ["$userId", user_id]}
                    ]}}},
                    {"$group": {
                        "_id": None,
                        "firstSolved": {"$min": "$submittedAt"},
                        "lastSolved":  {"$max": "$submittedAt"}
                    }}
                ],
                "as": "subsAgg"
            }},
            {"$addFields": {
                "firstSolved": {"$ifNull": [{"$arrayElemAt": ["$subsAgg.firstSolved", 0]}, None]},
                "lastSolved":  {"$ifNull": [{"$arrayElemAt": ["$subsAgg.lastSolved",  0]}, None]}
            }},
            {"$project": {"subsAgg": 0}}
        ]

    sort_key = {
        "title": "title",
        "difficulty": "difficulty",
        "firstSolved": "firstSolved",
        "lastSolved": "lastSolved"
    }.get(sort, "title")

    pipeline += [{"$sort": {sort_key: order}}, {"$skip": skip}, {"$limit": limit}]

    docs = list(db.problems.aggregate(pipeline))
    # Attach user customTags count (optional, simple count for now)
    if user_id:
        pid_map = {d["_id"]: d for d in docs}
        tag_counts = db.userProblemTags.aggregate([
            {"$match": {"userId": user_id, "problemId": {"$in": list(pid_map.keys())}}},
            {"$group": {"_id": "$problemId", "count": {"$sum": 1}}}
        ])
        for t in tag_counts:
            pid_map[t["_id"]]["customTagsCount"] = t["count"]

    # make JSON-friendly
    for d in docs:
        d["_id"] = str(d["_id"])
        for k in ("firstSolved", "lastSolved", "createdAt", "updatedAt"):
            if isinstance(d.get(k), datetime):
                d[k] = d[k].isoformat()

    # total count for pagination
    total = db.problems.count_documents(match)
    return jsonify({"items": docs, "limit": limit, "skip": skip, "total": total}), 200
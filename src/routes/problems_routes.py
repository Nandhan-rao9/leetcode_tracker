# src/routes/problems_routes.py
from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime
from ..db import db

bp_problems = Blueprint("problems", __name__)

def _to_iso(dt):
    if isinstance(dt, datetime):
        return dt.isoformat()
    return dt

@bp_problems.get("/problems")
def list_problems():
    """
    Query params:
      q: text search on title (regex, case-insensitive)
      difficulty: Easy|Medium|Hard
      tags: comma-separated (requires ALL)
      userId: for lastSolved + customTags
      sort: title|lastSolved|difficulty  (default: title)
      order: 1|-1                        (default: 1)
      skip: int                          (default: 0)
      limit: int                         (default: 50; max 200)
    """
    q = (request.args.get("q") or "").strip()
    difficulty = request.args.get("difficulty")
    tags = request.args.get("tags")
    sort = request.args.get("sort", "title")
    try:
        order = int(request.args.get("order", "1"))
    except ValueError:
        order = 1
    user_id = request.args.get("userId")
    try:
        skip = max(0, int(request.args.get("skip", "0")))
    except ValueError:
        skip = 0
    try:
        limit = min(200, max(1, int(request.args.get("limit", "50"))))
    except ValueError:
        limit = 50

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

    # Join last submission date for given user
    if user_id:
        pipeline += [
            {
                "$lookup": {
                    "from": "submissions",
                    "let": {"pid": "$_id"},
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$and": [
                                        {"$eq": ["$problemId", "$$pid"]},
                                        {"$eq": ["$userId", user_id]},
                                    ]
                                }
                            }
                        },
                        {"$sort": {"submittedAt": -1}},
                        {"$limit": 1},
                        {"$project": {"submittedAt": 1}},
                    ]
                }
            },
            {"$addFields": {"lastSolved": {"$ifNull": [{"$arrayElemAt": ["$submissionList.submittedAt", 0]}, None]}}},
            {"$project": {"submissionList": 0}},
        ]

        # Join user's custom tags for this problem
        pipeline += [
            {
                "$lookup": {
                    "from": "userProblemTags",
                    "let": {"pid": "$_id"},
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$and": [
                                        {"$eq": ["$problemId", "$$pid"]},
                                        {"$eq": ["$userId", user_id]},
                                    ]
                                }
                            }
                        },
                        {"$project": {"_id": 0, "tag": 1}},
                    ],
                    "as": "customTagsDocs",
                }
            },
            {"$addFields": {"customTags": {"$map": {"input": "$customTagsDocs", "as": "t", "in": "$$t.tag"}}}},
            {"$project": {"customTagsDocs": 0}},
        ]

    sort_key = {
        "title": "title",
        "difficulty": "difficulty",
        "lastSolved": "lastSolved",
    }.get(sort, "title")

    pipeline += [
        {"$sort": {sort_key: order, "_id": 1}},
        {"$skip": skip},
        {"$limit": limit},
        # project explicit fields incl. slug
        {
            "$project": {
                "_id": 1,
                "slug": 1,
                "title": 1,
                "url": 1,
                "difficulty": 1,
                "lcTags": 1,
                "customTags": {"$ifNull": ["$customTags", []]},
                "createdAt": 1,
                "updatedAt": 1,
                "lastSolved": 1,
            }
        },
    ]

    docs = list(db.problems.aggregate(pipeline))
    total = db.problems.count_documents(match)

    for d in docs:
        d["_id"] = str(d["_id"])
        if "createdAt" in d:
            d["createdAt"] = _to_iso(d["createdAt"])
        if "updatedAt" in d:
            d["updatedAt"] = _to_iso(d["updatedAt"])
        if "lastSolved" in d:
            d["lastSolved"] = _to_iso(d["lastSolved"])

    return jsonify({"items": docs, "skip": skip, "limit": limit, "total": total})


@bp_problems.get("/problems/missing-meta")
def problems_missing_meta():
    """
    Returns problems that need enrichment:
    - difficulty is null OR lcTags is empty OR title looks like a slug
    Now returns full docs (slug, title, url, difficulty, lcTags, timestamps).
    """
    from datetime import datetime

    def _to_iso(dt):
        return dt.isoformat() if isinstance(dt, datetime) else dt

    try:
        limit = min(500, max(1, int(request.args.get("limit", "200"))))
    except ValueError:
        limit = 200

    looks_like_slug = {"$regex": r"^[a-z0-9-]+$", "$options": "i"}

    cur = db.problems.find(
        {
            "$or": [
                {"difficulty": None},
                {"lcTags": {"$size": 0}},
                {"title": looks_like_slug},
            ]
        }
        # <- no projection here; return full doc
    ).limit(limit)

    items = []
    for doc in cur:
        doc["_id"] = str(doc["_id"])
        if "createdAt" in doc:
            doc["createdAt"] = _to_iso(doc["createdAt"])
        if "updatedAt" in doc:
            doc["updatedAt"] = _to_iso(doc["updatedAt"])
        items.append(doc)

    return jsonify({"count": len(items), "items": items})


@bp_problems.post("/problems/meta-bulk")
def problems_meta_bulk():
    """
    Body: { items: [{ slug, title, url, difficulty, lcTags: [] }] }
    Upserts meta for existing problems by slug.
    """
    data = request.get_json(force=True, silent=False) or {}
    items = data.get("items") or []
    if not isinstance(items, list) or not items:
        return jsonify(error="no_items"), 400

    updated = 0
    errors = []
    for it in items:
        slug = (it.get("slug") or "").strip()
        if not slug:
            errors.append({"slug": None, "reason": "missing slug"})
            continue
        try:
            res = db.problems.update_one(
                {"slug": slug},
                {
                    "$set": {
                        "title": it.get("title") or slug.replace("-", " ").title(),
                        "url": it.get("url") or f"https://leetcode.com/problems/{slug}/",
                        "difficulty": it.get("difficulty"),
                        "lcTags": it.get("lcTags") or [],
                        "updatedAt": datetime.utcnow(),
                    }
                },
            )
            if res.matched_count:
                updated += 1
            else:
                errors.append({"slug": slug, "reason": "not_found"})
        except Exception as e:
            errors.append({"slug": slug, "reason": str(e)})

    return jsonify(ok=True, updated=updated, errors=len(errors), errorSamples=errors[:10])

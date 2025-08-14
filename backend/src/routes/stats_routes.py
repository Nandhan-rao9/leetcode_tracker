from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from ..db import db

stats_bp = Blueprint("stats", __name__)

@stats_bp.get("/stats/overview")
def overview():
    user_id = request.args.get("userId")
    if not user_id:
        return jsonify(error="userId required"), 400

    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    # counts by difficulty (joined through problems)
    pipe_diff = [
        {"$match": {"userId": user_id}},
        {"$lookup": {
            "from": "problems",
            "localField": "problemId",
            "foreignField": "_id",
            "as": "p"
        }},
        {"$unwind": "$p"},
        {"$group": {"_id": "$p.difficulty", "count": {"$sum": 1}}},
    ]
    by_diff = {d["_id"] or "Unknown": d["count"] for d in db.submissions.aggregate(pipe_diff)}

    # solved per day (last 30d)
    pipe_daily = [
        {"$match": {"userId": user_id, "submittedAt": {"$gte": month_ago}}},
        {"$project": {"d": {"$dateToString": {"format": "%Y-%m-%d", "date": "$submittedAt"}}}},
        {"$group": {"_id": "$d", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    per_day = [{"date": d["_id"], "count": d["count"]} for d in db.submissions.aggregate(pipe_daily)]

    return jsonify({
        "byDifficulty": by_diff,
        "last30dDaily": per_day,
    }), 200

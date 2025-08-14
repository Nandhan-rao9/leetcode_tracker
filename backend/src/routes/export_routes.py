# src/routes/export_routes.py
from flask import Blueprint, request, Response
from io import StringIO
import csv
from datetime import datetime
from ..db import db

bp_export = Blueprint("export", __name__)

@bp_export.get("/export/csv")
def export_csv():
    user_id = request.args.get("userId")
    if not user_id:
        return {"error": "userId required"}, 400

    # join submissions -> problems -> notes (user-specific)
    subs = db.submissions.aggregate([
        {"$match": {"userId": user_id}},
        {"$lookup": {"from": "problems", "localField": "problemId", "foreignField": "_id", "as": "p"}},
        {"$unwind": "$p"},
        {"$lookup": {
            "from": "notes",
            "let": {"pid": "$problemId"},
            "pipeline": [
                {"$match": {"$expr": {"$and": [
                    {"$eq": ["$problemId", "$$pid"]},
                    {"$eq": ["$userId", user_id]}
                ]}}},
                {"$project": {"content": 1}}
            ],
            "as": "n"
        }},
        {"$addFields": {"note": {"$ifNull": [{"$arrayElemAt": ["$n.content", 0]}, ""]}}},
        {"$project": {"n": 0}},
        {"$sort": {"submittedAt": -1}}
    ])

    buf = StringIO()
    w = csv.writer(buf)
    w.writerow(["Date(UTC)", "Title", "Slug", "URL", "Difficulty", "LeetCodeTags", "Lang", "Note"])
    for s in subs:
        p = s["p"]
        w.writerow([
            s["submittedAt"].isoformat() if isinstance(s["submittedAt"], datetime) else s["submittedAt"],
            p.get("title",""),
            p.get("slug",""),
            p.get("url",""),
            p.get("difficulty","") or "",
            "; ".join(p.get("lcTags", [])),
            s.get("lang","") or "",
            s.get("note","") or ""
        ])

    csv_data = buf.getvalue()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": 'attachment; filename="leetcode_export.csv"'}
    )

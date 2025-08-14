# src/routes/notes_tags_routes.py
from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime
from ..db import db

bp_notes_tags = Blueprint("notes_tags", __name__)

def _oid(s: str): return ObjectId(s)

@bp_notes_tags.get("/notes/<problemId>")
def get_note(problemId):
    user_id = request.args.get("userId")
    if not user_id: return jsonify(error="userId required"), 400
    doc = db.notes.find_one({"userId": user_id, "problemId": _oid(problemId)})
    if not doc: return jsonify({"content": ""})
    return jsonify({
        "_id": str(doc["_id"]),
        "problemId": str(doc["problemId"]),
        "content": doc.get("content", ""),
        "updatedAt": doc.get("updatedAt").isoformat() if doc.get("updatedAt") else None
    })

@bp_notes_tags.post("/notes/<problemId>")
def upsert_note(problemId):
    user_id = request.args.get("userId")
    if not user_id: return jsonify(error="userId required"), 400
    data = request.get_json(force=True) or {}
    content = data.get("content", "")
    db.notes.update_one(
        {"userId": user_id, "problemId": _oid(problemId)},
        {"$set": {"content": content, "updatedAt": datetime.utcnow()},
         "$setOnInsert": {"createdAt": datetime.utcnow()}},
        upsert=True
    )
    return jsonify(ok=True)

@bp_notes_tags.get("/tags/<problemId>")
def list_tags(problemId):
    user_id = request.args.get("userId")
    if not user_id: return jsonify(error="userId required"), 400
    tags = list(db.userProblemTags.find({"userId": user_id, "problemId": _oid(problemId)}, {"tag": 1}))
    return jsonify(sorted([t["tag"] for t in tags]))

@bp_notes_tags.post("/tags/<problemId>")
def add_tag(problemId):
    user_id = request.args.get("userId")
    if not user_id: return jsonify(error="userId required"), 400
    tag = (request.get_json(force=True) or {}).get("tag", "").strip()
    if not tag: return jsonify(error="tag required"), 400
    db.userProblemTags.update_one(
        {"userId": user_id, "problemId": _oid(problemId), "tag": tag},
        {"$setOnInsert": {"createdAt": datetime.utcnow()}},
        upsert=True
    )
    return jsonify(ok=True)

@bp_notes_tags.delete("/tags/<problemId>")
def delete_tag(problemId):
    user_id = request.args.get("userId")
    tag = request.args.get("tag", "").strip()
    if not user_id or not tag: return jsonify(error="userId and tag required"), 400
    db.userProblemTags.delete_one({"userId": user_id, "problemId": _oid(problemId), "tag": tag})
    return jsonify(ok=True)

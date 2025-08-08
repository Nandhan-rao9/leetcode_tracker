from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime
from ..db import db

notes_tags_bp = Blueprint("notes_tags", __name__)

def _oid(s: str) -> ObjectId:
    return ObjectId(s)

@notes_tags_bp.get("/notes/<problemId>")
def get_note(problemId):
    user_id = request.args.get("userId")
    if not user_id:
        return jsonify(error="userId required"), 400

    doc = db.notes.find_one({"userId": user_id, "problemId": _oid(problemId)})
    if not doc:
        return jsonify({"content": ""}), 200

    return jsonify({
        "_id": str(doc["_id"]),
        "problemId": str(doc["problemId"]),
        "content": doc.get("content", ""),
        "updatedAt": doc.get("updatedAt").isoformat() if doc.get("updatedAt") else None
    })

@notes_tags_bp.post("/notes/<problemId>")
def upsert_note(problemId):
    user_id = request.args.get("userId")
    if not user_id:
        return jsonify(error="userId required"), 400

    data = request.get_json(force=True) or {}
    content = data.get("content", "")

    db.notes.update_one(
        {"userId": user_id, "problemId": _oid(problemId)},
        {"$set": {"content": content, "updatedAt": datetime.utcnow()},
         "$setOnInsert": {"createdAt": datetime.utcnow()}},
        upsert=True
    )
    return jsonify(ok=True), 200

@notes_tags_bp.post("/tags/<problemId>")
def add_tag(problemId):
    user_id = request.args.get("userId")
    if not user_id:
        return jsonify(error="userId required"), 400

    data = request.get_json(force=True) or {}
    tag = (data.get("tag") or "").strip()
    if not tag:
        return jsonify(error="tag required"), 400

    db.userProblemTags.update_one(
        {"userId": user_id, "problemId": _oid(problemId), "tag": tag},
        {"$setOnInsert": {"createdAt": datetime.utcnow()}},
        upsert=True
    )
    return jsonify(ok=True), 200

@notes_tags_bp.delete("/tags/<problemId>")
def delete_tag(problemId):
    user_id = request.args.get("userId")
    if not user_id:
        return jsonify(error="userId required"), 400
    tag = (request.args.get("tag") or "").strip()
    if not tag:
        return jsonify(error="tag required"), 400

    db.userProblemTags.delete_one({"userId": user_id, "problemId": _oid(problemId), "tag": tag})
    return jsonify(ok=True), 200

from flask import Blueprint, request, jsonify, current_app
from pydantic import ValidationError
from pymongo import ReturnDocument
from datetime import datetime
from ..db import db
from ..schemas import ImportBatch
import hmac, hashlib
from ..config import EXTENSION_SHARED_SECRET

bp = Blueprint("imports", __name__)

def _verify_hmac_or_400(raw_body: bytes):
    sig = request.headers.get("X-Signature", "")
    if not sig.startswith("sha256="):
        return False
    provided = sig.split("=", 1)[1]
    digest = hmac.new(EXTENSION_SHARED_SECRET.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(provided, digest)

@bp.post("/import/leetcode")
def import_leetcode():
    raw = request.get_data()
    # if not _verify_hmac_or_400(raw):
    #     return jsonify(error="unauthorized", message="bad signature"), 401

    try:
        payload = request.get_json(force=True)
        batch = ImportBatch.model_validate(payload)
    except ValidationError as ve:
        return jsonify(error="validation_error", details=ve.errors()), 400
    except Exception as e:
        return jsonify(error="invalid_json", details=str(e)), 400

    inserted = 0
    upserted = 0
    skipped = 0
    errors = []

    for item in batch.items:
        try:
            p = db.problems.find_one_and_update(
                {"slug": item.slug},
                {"$set": {
                    "title": item.title,
                    "url": item.url,
                    "difficulty": item.difficulty,
                    "lcTags": item.lcTags,
                    "updatedAt": datetime.utcnow()
                 },
                 "$setOnInsert": {"createdAt": datetime.utcnow()}},
                 upsert=True,
                 return_document=ReturnDocument.AFTER
            )
            problem_id = p["_id"]
            # dedupe by triple
            exists = db.submissions.find_one({
                "userId": batch.userId,
                "problemId": problem_id,
                "submittedAt": item.submittedAt
            }, {"_id": 1})
            if exists:
                skipped += 1
            else:
                db.submissions.insert_one({
                    "userId": batch.userId,
                    "problemId": problem_id,
                    "status": "AC",
                    "lang": item.lang,
                    "submittedAt": item.submittedAt,
                    "ingestedAt": datetime.utcnow(),
                    "source": "extension_backfill"
                })
                inserted += 1
            upserted += 1
        except Exception as e:
            errors.append({"slug": item.slug, "reason": str(e)})

    return jsonify(ok=True, stats={
        "problemsProcessed": upserted,
        "insertedSubmissions": inserted,
        "duplicatesSkipped": skipped,
        "errors": len(errors)
    }, errors=errors[:10]), 200

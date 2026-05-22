import time
from flask import Blueprint, request, jsonify
from utils.db import users_col
from services.leetcode_client import LeetCodeClient
from routes.ingest_user import archive_solved_problems

user_bp = Blueprint("user", __name__)

@user_bp.route("/api/user/init", methods=["POST"])
def init_user():
    data = request.get_json()
    username = data["username"]
    lc_user = data["leetcode_username"]

    users_col.update_one(
        {"_id": username},
        {"$set": {
            "leetcode_username": lc_user,
            "ingestion_status": "ingesting",
            "last_ingested_at": None,
            "created_at": time.time()
        }},
        upsert=True
    )

    client = LeetCodeClient(
        session=data["session"],
        csrf=data["csrftoken"]
    )

    # Store client temporarily
    from flask import current_app
    current_app.config["LC_CLIENT"] = client

    try:
        archive_solved_problems(username)

        users_col.update_one(
            {"_id": username},
            {"$set": {
                "ingestion_status": "ready",
                "last_ingested_at": time.time()
            }}
        )
    except Exception:
        users_col.update_one(
            {"_id": username},
            {"$set": {"ingestion_status": "error"}}
        )
        return jsonify({"status": "error"}), 500

    return jsonify({"status": "ok"})

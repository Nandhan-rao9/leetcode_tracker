from http import client
import time
from flask import Blueprint, jsonify, current_app
# Added 'db' to the import list below
from utils.db import db, problems_master, user_solved_col

user_ingest_bp = Blueprint("user_ingest", __name__)

@user_ingest_bp.route("/api/archive/solved/<username>", methods=["POST"])
def archive_solved_problems(username):
    from utils.db import db
    client = current_app.config.get("LEETCODE_CLIENT")
    if not client:
        return jsonify({"error": "LeetCode client not initialized"}), 400

    archive_col = db[f"archive_solved_{username}"] 

    # 1. Get slugs
    slugs = client.fetch_all_accepted_slugs()
    
    if not slugs:
        return jsonify({"status": "error", "message": "No solved problems found or API error."}), 400

    # 2. Get titles
    problem_details = client.fetch_titles_directly(slugs)

    # 3. Save to MongoDB
    inserted_count = 0
    for p in problem_details:
        archive_col.update_one(
            {"slug": p["slug"]},
            {"$set": {
                "title": p["title"],
                "slug": p["slug"],
                "updated_at": time.time()
            }},
            upsert=True
        )
        inserted_count += 1

    return jsonify({
        "status": "success",
        "total_solved_found": len(slugs),
        "titles_archived": inserted_count
    })
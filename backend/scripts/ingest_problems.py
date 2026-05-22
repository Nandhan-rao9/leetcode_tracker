# backend/scripts/ingest_problems.py

from datetime import datetime
from utils.db import db
from services.leetcode_client import make_leetcode_request

problems_col = db["problems_master"]

PROBLEMSET_QUERY = """
query problemsetQuestionList($limit: Int!, $skip: Int!) {
  problemsetQuestionList(
    categorySlug: ""
    limit: $limit
    skip: $skip
    filters: {}
  ) {
    total
    questions {
      acRate
      difficulty
      frontendQuestionId
      paidOnly
      title
      titleSlug
      hasSolution
      hasVideoSolution
      topicTags {
        name
        slug
      }
    }
  }
}
"""

BATCH_SIZE = 100

def ingest_all_problems():
    skip = 0
    total = None
    inserted = 0

    print("Starting LeetCode problem ingestion...")

    while total is None or skip < total:
        data = make_leetcode_request(
            PROBLEMSET_QUERY,
            {"limit": BATCH_SIZE, "skip": skip}
        )

        plist = data["problemsetQuestionList"]
        total = plist["total"]
        questions = plist["questions"]

        for q in questions:
            doc = {
                "_id": q["titleSlug"],   # PRIMARY KEY
                "frontendQuestionId": int(q["frontendQuestionId"]),
                "title": q["title"],
                "difficulty": q["difficulty"],
                "acRate": round(q["acRate"], 2),
                "paidOnly": q["paidOnly"],
                "hasSolution": q["hasSolution"],
                "hasVideoSolution": q["hasVideoSolution"],

                # FAST FILTERING
                "topics": [t["slug"] for t in q["topicTags"]],

                # UI / analytics
                "topic_meta": q["topicTags"],

                # CSV enrichment fields (empty for now)
                "companies": [],
                "by_company": {},
                "num_occur": 0,

                "last_updated": datetime.utcnow()
            }

            problems_col.update_one(
                {"_id": doc["_id"]},
                {"$set": doc},
                upsert=True
            )

            inserted += 1

        skip += BATCH_SIZE
        print(f"Synced {min(skip, total)} / {total}")

    print(f"Done. Total problems synced: {inserted}")


if __name__ == "__main__":
    ingest_all_problems()

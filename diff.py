import os, re, time, random, requests
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME   = os.getenv("DB_NAME", "lc")
COLL_NAME = os.getenv("COLLECTION", "problems_min")

client = MongoClient(MONGO_URI)
col = client[DB_NAME][COLL_NAME]

GQL_URL = "https://leetcode.com/graphql/"
QUERY = """
query questionData($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    difficulty
    topicTags { name }
  }
}
"""

def url_to_slug(url: str) -> str | None:
    m = re.search(r"/problems/([^/]+)/?", url or "")
    return m.group(1) if m else None

def fetch_meta(slug: str, retries: int = 4):
    for attempt in range(retries + 1):
        try:
            r = requests.post(
                GQL_URL,
                json={"query": QUERY, "variables": {"titleSlug": slug}, "operationName": "questionData"},
                timeout=20,
                headers={"content-type": "application/json", "referer": "https://leetcode.com/"},
            )
            data = r.json()
            q = (data.get("data") or {}).get("question") or {}
            diff = q.get("difficulty")
            tags = [t["name"] for t in (q.get("topicTags") or [])]
            return diff, tags
        except Exception:
            if attempt == retries:
                return None, []
            time.sleep(0.6 * (2 ** attempt) + random.random() * 0.2)

def backfill(limit: int | None = None):
    query = {
        "$or": [
            {"difficulty": {"$exists": False}},
            {"difficulty": None},
            {"lcTags": {"$exists": False}},
            {"lcTags": []},
        ]
    }
    projection = {"problem_link": 1}
    cursor = col.find(query, projection)
    if limit:
        cursor = cursor.limit(limit)

    checked = updated = 0
    for doc in cursor:
        checked += 1
        link = doc.get("problem_link")
        slug = url_to_slug(link)
        if not slug:
            continue

        diff, tags = fetch_meta(slug)
        set_fields = {}
        if diff: set_fields["difficulty"] = diff
        if tags: set_fields["lcTags"] = tags
        if set_fields:
            set_fields["updatedAt"] = datetime.utcnow()
            col.update_one({"_id": doc["_id"]}, {"$set": set_fields})
            updated += 1
            print(f"✔ {slug} -> {diff or '—'} / {len(tags)} tags")
        else:
            print(f"… {slug}: no metadata")

        time.sleep(0.25 + random.random() * 0.15)  # be polite to LC

    print(f"Checked {checked}, updated {updated} docs.")

if __name__ == "__main__":
    # bump limit if needed; None processes all matching docs
    backfill(limit=None)

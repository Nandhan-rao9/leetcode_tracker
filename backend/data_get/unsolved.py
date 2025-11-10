# push_unsolved_to_mongo.py
import json
import pymongo
from pymongo.server_api import ServerApi

# --- CONFIGURATION ---
MONGO_CONNECTION_STRING = ""
DB_NAME = "leetcode_project"
UNSOLVED_COLLECTION = "unsolved_problems"

SOLVED_FILE = "my_solved_problems_cleaned.json"
ALL_FILE = "leetcode_cleaned_topics.json"
# ---------------------


def normalize_topics(topics):
    """Convert topic names to lowercase and strip spaces."""
    return [t.lower().strip() for t in topics if t]


def get_unsolved_problems():
    """Find problems that are not solved yet."""
    with open(ALL_FILE, "r", encoding="utf-8") as f:
        all_problems = json.load(f)
    with open(SOLVED_FILE, "r", encoding="utf-8") as f:
        solved = json.load(f)

    solved_slugs = {p["slug"] for p in solved}
    unsolved = []

    for prob in all_problems:
        slug = prob["slug"]
        if slug not in solved_slugs:
            all_topics = normalize_topics(prob["all_topics"])
            unsolved.append({
                "title": prob["title"],
                "slug": slug,
                "difficulty": prob["difficulty"],
                "main_topic": prob["main_topic"].lower().strip() if prob["main_topic"] else None,
                "secondary_topic": prob["secondary_topic"].lower().strip() if prob["secondary_topic"] else None,
                "all_topics": all_topics,
                "link": f"https://leetcode.com/problems/{slug}/"
            })

    print(f"🧮 Found {len(unsolved)} unsolved problems.")
    return unsolved


def push_to_mongo(data):
    """Push unsolved problems to the unsolved collection."""
    try:
        client = pymongo.MongoClient(MONGO_CONNECTION_STRING, server_api=ServerApi('1'))
        client.admin.command('ping')
        print("✅ Connected to MongoDB.")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return

    db = client[DB_NAME]
    collection = db[UNSOLVED_COLLECTION]

    print(f"🧹 Clearing old data from '{UNSOLVED_COLLECTION}'...")
    collection.delete_many({})

    print(f"📤 Inserting {len(data)} documents...")
    collection.insert_many(data)
    print(f"🚀 Upload complete! Collection '{UNSOLVED_COLLECTION}' is ready.")

    client.close()


if __name__ == "__main__":
    unsolved = get_unsolved_problems()
    push_to_mongo(unsolved)

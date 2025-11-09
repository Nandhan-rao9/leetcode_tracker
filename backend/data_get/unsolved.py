import json
import pymongo
from pymongo.server_api import ServerApi

# --- CONFIGURATION ---
MONGO_CONNECTION_STRING = "mongodb+srv://22311a1903:6iR48dJ7qRRipFlh@cluster0.2nkd33g.mongodb.net/?appName=Cluster0"
DB_NAME = "leetcode_project"
SOLVED_COLLECTION = "solved_problems"
UNSOLVED_COLLECTION = "unsolved_problems"

SOLVED_FILE = "my_solved_problems_cleaned.json"   # Solved ones
ALL_FILE = "leetcode_cleaned_topics.json"         # All problems
# ---------------------


def get_unsolved_problems():
    """Compare all problems vs solved and return unsolved list."""
    with open(ALL_FILE, "r", encoding="utf-8") as f:
        all_problems = json.load(f)
    with open(SOLVED_FILE, "r", encoding="utf-8") as f:
        solved = json.load(f)

    solved_slugs = {p["slug"] for p in solved}
    unsolved = []

    for prob in all_problems:
        slug = prob["slug"]
        if slug not in solved_slugs:
            unsolved.append({
                "title": prob["title"],
                "slug": slug,
                "difficulty": prob["difficulty"],
                "main_topic": prob["main_topic"],
                "secondary_topic": prob["secondary_topic"],
                "all_topics": prob["all_topics"],
                "link": f"https://leetcode.com/problems/{slug}/"
            })

    print(f"🧮 Found {len(unsolved)} unsolved problems.")
    return unsolved


def push_unsolved_to_mongo(data):
    """Push unsolved problems into MongoDB under a new collection."""
    try:
        client = pymongo.MongoClient(MONGO_CONNECTION_STRING, server_api=ServerApi('1'))
        client.admin.command('ping')
        print("✅ Connected to MongoDB successfully.")
    except Exception as e:
        print("❌ Could not connect to MongoDB:", e)
        return

    db = client[DB_NAME]
    collection = db[UNSOLVED_COLLECTION]

    print(f"🧹 Clearing old data from '{UNSOLVED_COLLECTION}'...")
    collection.delete_many({})

    print(f"📤 Inserting {len(data)} unsolved problems...")
    collection.insert_many(data)
    print("🚀 Upload complete!")

    client.close()


if __name__ == "__main__":
    unsolved = get_unsolved_problems()
    push_unsolved_to_mongo(unsolved)

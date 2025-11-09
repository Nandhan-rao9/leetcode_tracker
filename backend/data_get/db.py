import json
import pymongo
from pymongo.server_api import ServerApi

# --- CONFIGURATION ---
MONGO_CONNECTION_STRING = ""
DB_NAME = "leetcode_project"
COLLECTION_NAME = "solved_problems"

SOLVED_FILE = "my_solved_problems_final.json"
CLEANED_FILE = "leetcode_cleaned_topics.json"
OUTPUT_FILE = "my_solved_problems_cleaned.json"
# ---------------------

def merge_data():
    """Merge your solved problems with cleaned topic data."""
    with open(SOLVED_FILE, "r", encoding="utf-8") as f1:
        solved = json.load(f1)
    with open(CLEANED_FILE, "r", encoding="utf-8") as f2:
        cleaned = json.load(f2)

    # Create lookup by titleSlug
    cleaned_map = {item["slug"]: item for item in cleaned}

    merged = []
    for s in solved:
        slug = s["link"].split("/problems/")[-1].strip("/")
        base = cleaned_map.get(slug)

        if base:
            merged.append({
                "title": s["title"],
                "slug": slug,
                "difficulty": base["difficulty"],
                "main_topic": base["main_topic"],
                "secondary_topic": base["secondary_topic"],
                "all_topics": base["all_topics"],
                "submittedDate": s["submittedDate"],
                "link": s["link"]
            })
        else:
            # fallback if slug not found in cleaned list
            merged.append({
                "title": s["title"],
                "slug": slug,
                "difficulty": s.get("difficulty"),
                "main_topic": None,
                "secondary_topic": None,
                "all_topics": [t.get("name") for t in s.get("topicTags", [])],
                "submittedDate": s["submittedDate"],
                "link": s["link"]
            })

    # Save locally
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2)

    print(f"✅ Merged {len(merged)} problems → saved to '{OUTPUT_FILE}'")
    return merged


def upload_to_mongo(data):
    """Upload merged data to MongoDB."""
    try:
        client = pymongo.MongoClient(MONGO_CONNECTION_STRING, server_api=ServerApi('1'))
        client.admin.command('ping')
        print("✅ Connected to MongoDB successfully")
    except Exception as e:
        print("❌ Could not connect to MongoDB:", e)
        return

    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    # Clear old data
    print("🧹 Clearing old data...")
    collection.delete_many({})

    # Insert new
    print(f"📤 Inserting {len(data)} documents...")
    collection.insert_many(data)
    print("🚀 Upload complete!")
    client.close()


if __name__ == "__main__":
    merged_data = merge_data()
    upload_to_mongo(merged_data)

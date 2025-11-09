import pymongo
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

mongo_uri = os.getenv("MONGO_URI")
db_name = "leetcode_project"
collection_name = "solved_problems"

try:
    client = pymongo.MongoClient(mongo_uri)
    client.admin.command('ping')
    print("MongoDB connection successful.")
except Exception as e:
    print(f"MongoDB connection failed: {e}")
    client = None

# Get the database and solved collection
db = client[db_name]
solved_problems_collection = db[collection_name]

# --- NEW: Load the "all problems" JSON file ---
all_problems_list = []
try:
    # Gets the path to the 'backend' folder
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_file_path = os.path.join(base_dir, 'all_leetcode_problems.json')

    with open(json_file_path, "r", encoding="utf-8") as f:
        all_problems_data = json.load(f)
        all_problems_list = all_problems_data.get('data', {}).get('problemsetQuestionList', {}).get('questions', [])
    print(f"Successfully loaded {len(all_problems_list)} problems from all_leetcode_problems.json")

except FileNotFoundError:
    print("WARNING: 'all_leetcode_problems.json' not found. 'Find Similar' API will not work.")
except Exception as e:
    print(f"Error loading 'all_leetcode_problems.json': {e}")
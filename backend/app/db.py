import pymongo
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

mongo_uri = os.getenv("MONGO_URI")

# --- YOUR NEW CONFIGURATION ---
DB_NAME = "leetcode_project"
SOLVED_COLLECTION = "solved_problems"
UNSOLVED_COLLECTION = "unsolved_problems" # <-- NEW
# ------------------------------

try:
    client = pymongo.MongoClient(mongo_uri)
    client.admin.command('ping')
    print("MongoDB connection successful.")
except Exception as e:
    print(f"MongoDB connection failed: {e}")
    client = None

# Get the database
db = client[DB_NAME]

# Get our collections
solved_problems_collection = db[SOLVED_COLLECTION]
unsolved_problems_collection = db[UNSOLVED_COLLECTION] # <-- NEW

# We no longer load the JSON file, saving a lot of memory!
print(f"Connected to database '{DB_NAME}' and collections.")
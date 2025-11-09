import pymongo
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

mongo_uri = os.getenv("MONGO_URI")
db_name = "leetcode_project"
collection_name = "solved_problems"

try:
    client = pymongo.MongoClient(mongo_uri)
    # Ping to confirm connection
    client.admin.command('ping')
    print("MongoDB connection successful.")
except Exception as e:
    print(f"MongoDB connection failed: {e}")
    client = None

# Get the database
db = client[db_name]
# Get the collection
solved_problems_collection = db[collection_name]
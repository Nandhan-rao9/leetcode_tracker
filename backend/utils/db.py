# backend/utils/db.py
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "leetcode_project")

if not MONGO_URI:
    raise RuntimeError("MONGO_URI not set in environment (.env)")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

solved_col = db["solved_problems"]
unsolved_col = db["unsolved_problems"]

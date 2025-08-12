# src/db.py
from pymongo import MongoClient, ASCENDING
from .config import MONGO_URI, DB_NAME

# Force no TLS for localhost dev
_client = MongoClient(MONGO_URI, tls=False)
db = _client[DB_NAME]

def create_indexes():
    db.problems.create_index([("slug", ASCENDING)], unique=True)
    db.submissions.create_index([("userId", ASCENDING), ("problemId", ASCENDING), ("submittedAt", ASCENDING)])
    db.notes.create_index([("userId", ASCENDING), ("problemId", ASCENDING)])
    db.notes.create_index([("content", "text")])

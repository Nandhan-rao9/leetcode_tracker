# backend/utils/db.py
from pymongo import MongoClient, ASCENDING
import os

client = MongoClient(os.getenv("MONGO_URI"))
db = client["new_lp"]

problems_master = db["problems_master"]
users_col = db["users"]

def user_solved_col(username):
    return db[f"archive_solved_{username}"]

def create_indexes():
    """Create database indexes for optimal performance."""
    try:
        # Users collection indexes
        users_col.create_index("email", unique=True)
        users_col.create_index("username", unique=True)

        # Problems master collection indexes
        problems_master.create_index("companies")
        problems_master.create_index("difficulty")
        problems_master.create_index("topics")

        print("[DB] Indexes created successfully")
    except Exception as e:
        print(f"[DB] Error creating indexes: {e}")


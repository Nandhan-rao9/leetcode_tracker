# backend/utils/db.py
from pymongo import MongoClient
import os

client = MongoClient(os.getenv("MONGO_URI"))
db = client["new_lp"]

problems_master = db["problems_master"]

def user_solved_col(username):
    return db[f"archive_solved_{username}"]


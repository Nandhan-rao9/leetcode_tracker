"""
Quick script to create user account for nandhan_rao
"""

import sys
sys.path.append('.')

from utils.db import users_col
from utils.crypto import encrypt_credential
import bcrypt
import time
import os
from dotenv import load_dotenv

load_dotenv()

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# User credentials
email = "nandhan_rao@leetbuddy.com"
password = "Password123"
username = "nandhan_rao"

# Check if user already exists
existing_user = users_col.find_one({"username": username})

if existing_user:
    print(f"⚠ User '{username}' already exists!")
    print(f"Email: {existing_user.get('email')}")
    print("\nUpdating password...")

    users_col.update_one(
        {"_id": existing_user["_id"]},
        {"$set": {
            "password_hash": hash_password(password),
            "updated_at": time.time()
        }}
    )
    print("✓ Password updated!")
else:
    print(f"Creating new user account for '{username}'...")

    # Get LeetCode credentials from .env if available
    lc_session = os.getenv("LEETCODE_SESSION", "")
    lc_csrf = os.getenv("LEETCODE_CSRF", "")

    user_doc = {
        "email": email,
        "password_hash": hash_password(password),
        "username": username,
        "leetcode_username": username,
        "leetcode_session_encrypted": encrypt_credential(lc_session) if lc_session else None,
        "leetcode_csrf_encrypted": encrypt_credential(lc_csrf) if lc_csrf else None,
        "ingestion_status": "ready",
        "last_ingested_at": time.time(),
        "created_at": time.time(),
        "updated_at": time.time()
    }

    result = users_col.insert_one(user_doc)
    print(f"✓ User created with ID: {result.inserted_id}")

print("\n" + "="*60)
print("LOGIN CREDENTIALS")
print("="*60)
print(f"Username: {username}")
print(f"Email: {email}")
print(f"Password: {password}")
print("="*60)
print("\nYou can now login at: http://localhost:3000")
print("Your existing data collection 'archive_solved_nandhan_rao' is linked!")

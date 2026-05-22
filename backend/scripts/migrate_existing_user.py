"""
Migration script to create a user account for existing data.
Converts hardcoded 'nandhan_rao' data to authenticated user.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path so we can import from utils
sys.path.append(str(Path(__file__).parent.parent))

from utils.db import db, users_col
from utils.crypto import encrypt_credential
import bcrypt
import time
from dotenv import load_dotenv

load_dotenv()

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def migrate():
    """Migrate existing nandhan_rao data to authenticated user."""
    print("=" * 60)
    print("LeetCode Tracker - User Migration Script")
    print("=" * 60)
    print()

    # Check if nandhan_rao collection exists
    existing_username = "nandhan_rao"
    collection_name = f"archive_solved_{existing_username}"

    if collection_name not in db.list_collection_names():
        print(f"❌ No data found for '{existing_username}'")
        print(f"   Collection '{collection_name}' does not exist.")
        print()
        return

    # Count existing problems
    problem_count = db[collection_name].count_documents({})
    print(f"✓ Found existing data for '{existing_username}'")
    print(f"  {problem_count} solved problems in collection")
    print()

    # Check if user already exists
    existing_user = users_col.find_one({"username": existing_username})
    if existing_user:
        print(f"⚠ User '{existing_username}' already exists in the database!")
        print(f"  Email: {existing_user.get('email')}")
        print(f"  Created: {time.ctime(existing_user.get('created_at'))}")
        print()
        response = input("Do you want to continue and update this user? (y/n): ")
        if response.lower() != 'y':
            print("Migration cancelled.")
            return
        print()

    # Collect user information
    print("Enter details for the new authenticated user:")
    print("-" * 60)

    email = input("Email address: ").strip()
    if not email:
        print("❌ Email is required")
        return

    password = input("Password (min 8 chars, include upper/lower/digit): ").strip()
    if len(password) < 8:
        print("❌ Password must be at least 8 characters")
        return

    # Optional: Get LeetCode credentials
    print()
    print("LeetCode Credentials (optional - press Enter to skip):")
    print("-" * 60)

    lc_username = input(f"LeetCode username [{existing_username}]: ").strip() or existing_username
    lc_session = input("LEETCODE_SESSION cookie (from browser): ").strip()
    lc_csrf = input("csrftoken cookie (from browser): ").strip()

    # If not provided, try to get from environment
    if not lc_session:
        lc_session = os.getenv("LEETCODE_SESSION", "")
    if not lc_csrf:
        lc_csrf = os.getenv("LEETCODE_CSRF", "")

    print()
    print("Creating user account...")
    print("-" * 60)

    # Create or update user document
    user_doc = {
        "email": email,
        "password_hash": hash_password(password),
        "username": existing_username,
        "leetcode_username": lc_username,
        "leetcode_session_encrypted": encrypt_credential(lc_session) if lc_session else None,
        "leetcode_csrf_encrypted": encrypt_credential(lc_csrf) if lc_csrf else None,
        "ingestion_status": "ready",
        "last_ingested_at": time.time(),
        "created_at": existing_user.get("created_at", time.time()) if existing_user else time.time(),
        "updated_at": time.time()
    }

    if existing_user:
        # Update existing user
        users_col.update_one(
            {"_id": existing_user["_id"]},
            {"$set": user_doc}
        )
        print(f"✓ Updated existing user account")
        user_id = existing_user["_id"]
    else:
        # Insert new user
        result = users_col.insert_one(user_doc)
        print(f"✓ Created new user account")
        user_id = result.inserted_id

    print()
    print("=" * 60)
    print("Migration Summary")
    print("=" * 60)
    print(f"✓ User ID: {user_id}")
    print(f"✓ Email: {email}")
    print(f"✓ Username: {existing_username}")
    print(f"✓ LeetCode Username: {lc_username}")
    print(f"✓ Solved Problems Collection: {collection_name}")
    print(f"✓ Problem Count: {problem_count}")
    print()
    print("✓ Migration completed successfully!")
    print()
    print("You can now login at the frontend using:")
    print(f"  Email: {email}")
    print(f"  Password: ********")
    print()

if __name__ == "__main__":
    try:
        migrate()
    except KeyboardInterrupt:
        print("\n\nMigration cancelled by user.")
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()

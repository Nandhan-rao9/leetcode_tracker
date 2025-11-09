import json
import pymongo
import os
from pymongo.server_api import ServerApi

# --- CONFIGURATION ---


# 1. PASTE YOUR MONGODB CONNECTION STRING HERE
# (Make sure to replace <password> with your actual password)
MONGO_CONNECTION_STRING = "YOUR_STRING"

# 2. Set your database and collection names
DB_NAME = "leetcode_project"
COLLECTION_NAME = "solved_problems"

# 3. The data file you just created
JSON_FILE_NAME = "my_solved_problems_final.json"

# ---------------------

def push_data_to_mongo():
    print("Attempting to connect to MongoDB...")
    
    # Connect to MongoDB
    try:
        # Create a new client and connect to the server
        client = pymongo.MongoClient(MONGO_CONNECTION_STRING, server_api=ServerApi('1'))
        
        # Send a ping to confirm a successful connection
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        
    except Exception as e:
        print(f"❌ ERROR: Could not connect to MongoDB. Check your connection string.")
        print(f"Details: {e}")
        return

    # Access your database and collection
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    # Load the JSON data from your file
    print(f"Loading data from '{JSON_FILE_NAME}'...")
    try:
        with open(JSON_FILE_NAME, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ ERROR: File not found: '{JSON_FILE_NAME}'")
        print("Please run 'process_data.py' first.")
        return
    except json.JSONDecodeError:
        print(f"❌ ERROR: Could not read '{JSON_FILE_NAME}'. Is it a valid JSON?")
        return

    if not data:
        print("⚠️ Warning: JSON file is empty. Nothing to upload.")
        return

    # --- Push data to MongoDB ---
    try:
        # Step 1: Clear the entire collection to avoid duplicates
        print(f"Clearing old data from collection '{COLLECTION_NAME}'...")
        delete_result = collection.delete_many({})
        print(f"Deleted {delete_result.deleted_count} old documents.")

        # Step 2: Insert the new data
        print(f"Inserting {len(data)} new documents...")
        insert_result = collection.insert_many(data)
        print(f"Successfully inserted {len(insert_result.inserted_ids)} documents.")
        
        print("\n--- 🚀 SUCCESS! ---")
        print("Your data is now in MongoDB.")

    except Exception as e:
        print(f"❌ ERROR: An error occurred during the database operation.")
        print(f"Details: {e}")
    
    finally:
        client.close()
        print("Connection to MongoDB closed.")

# --- Run the script ---
if __name__ == "__main__":
    if "PASTE_YOUR" in MONGO_CONNECTION_STRING or "<password>" in MONGO_CONNECTION_STRING:
        print("🚨 ERROR: Please paste your MongoDB Connection String into the script.")
    else:
        # First, check if you have the pymongo library
        try:
            import pymongo
        except ImportError:
            print("❌ ERROR: 'pymongo' library not found.")
            print("Please install it by running: pip install pymongo[srv]")
        else:
            push_data_to_mongo()
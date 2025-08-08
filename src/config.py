import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "leetcode_tracker")
EXTENSION_SHARED_SECRET = os.getenv("EXTENSION_SHARED_SECRET", "change-me")
PORT = int(os.getenv("PORT", "8080"))
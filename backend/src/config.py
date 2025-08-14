import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://leetcode:NandhanRao@cluster0.fqo5dxz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DB_NAME = os.getenv("DB_NAME", "leetcode_tracker")
EXTENSION_SHARED_SECRET = os.getenv("EXTENSION_SHARED_SECRET", "my-key")
PORT = int(os.getenv("PORT", "8080"))
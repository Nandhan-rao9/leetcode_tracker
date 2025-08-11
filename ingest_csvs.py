import os, glob, csv
from pymongo import MongoClient, UpdateOne
from dotenv import load_dotenv

# ---- config ----
FOLDER = "companies_csv"   # where your downloaded CSVs live

# Accept common header variants from that repo
NAME_KEYS  = ["problem_name", "Problem Name", "name", "Title"]
LINK_KEYS  = ["problem_link", "Problem Link", "link", "URL", "url"]
OCC_KEYS   = ["num_occur", "Num Occur", "Frequency", "Count", "Occurrences"]

def pick(row, keys):
    for k in keys:
        if k in row and row[k]:
            return row[k]
    return ""

def to_int(x):
    try: return int(str(x).strip())
    except: return 0

# ---- connect ----
load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME     = os.getenv("DB_NAME", "lc")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]
col = db.problems_min

# indexes (safe to run repeatedly)
col.create_index([("problem_link", 1)], unique=True)
col.create_index([("problem_name", "text")])
col.create_index([("num_occur", 1)])

def ingest_folder(folder=FOLDER):
    files = glob.glob(os.path.join(folder, "*.csv"))
    total_changed = 0

    for path in files:
        ops = []
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                problem_name = pick(row, NAME_KEYS).strip()
                problem_link = pick(row, LINK_KEYS).strip()
                num_occur    = to_int(pick(row, OCC_KEYS))

                # skip malformed rows
                if not problem_link or not problem_name:
                    continue

                doc = {
                    "problem_link": problem_link,
                    "problem_name": problem_name,
                    "num_occur": num_occur
                }
                ops.append(UpdateOne(
                    {"problem_link": problem_link},
                    {"$set": doc},
                    upsert=True
                ))

        if ops:
            res = col.bulk_write(ops, ordered=False)
            total_changed += res.upserted_count + res.modified_count
            print(f"{os.path.basename(path)} -> {res.upserted_count + res.modified_count} upserted/updated")

    print("Total changed:", total_changed)

if __name__ == "__main__":
    ingest_folder()

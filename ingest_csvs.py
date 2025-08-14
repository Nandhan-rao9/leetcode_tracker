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

def company_from_path(path: str) -> str:
    base = os.path.basename(path)
    name, _ = os.path.splitext(base)
    name = name.replace("_", " ").replace("-", " ").strip()
    # keep custom caps if present; else Title Case
    return " ".join(w if any(c.isupper() for c in w) else w.title() for w in name.split())

# ---- connect ----
load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME     = os.getenv("DB_NAME", "lc")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]
col = db.problems_min

# indexes (idempotent)
col.create_index([("problem_link", 1)], unique=True)
col.create_index([("problem_name", "text")])
col.create_index([("companies", 1)])
col.create_index([("num_occur", 1)])

def ingest_folder(folder=FOLDER):
    files = glob.glob(os.path.join(folder, "*.csv"))
    total_changed = 0

    for path in files:
        ops = []
        company = company_from_path(path)

        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                problem_name = pick(row, NAME_KEYS).strip()
                problem_link = pick(row, LINK_KEYS).strip()
                this_count   = to_int(pick(row, OCC_KEYS))

                if not problem_link or not problem_name:
                    continue

                # Build a one-key object: { "<Company>": <count> }
                company_obj = [{ "k": company, "v": this_count }]

                # Update pipeline (safe for upsert + merge)
                ops.append(UpdateOne(
                    {"problem_link": problem_link},
                    [
                        # ensure basic fields exist/updated
                        {"$set": {
                            "problem_link": problem_link,
                            "problem_name": problem_name
                        }},
                        # merge per-company count into by_company
                        {"$set": {
                            "by_company": {
                                "$mergeObjects": [
                                    { "$ifNull": ["$by_company", {}] },
                                    { "$arrayToObject": [ company_obj ] }
                                ]
                            }
                        }},
                        # keep companies array in sync with keys of by_company
                        {"$set": {
                            "companies": {
                                "$setUnion": [
                                    { "$ifNull": ["$companies", []] },
                                    [ company ]
                                ]
                            }
                        }},
                        # recompute total occurrences = sum of by_company values
                        {"$set": {
                            "num_occur": {
                                "$sum": {
                                    "$map": {
                                        "input": { "$objectToArray": { "$ifNull": ["$by_company", {}] } },
                                        "as": "kv",
                                        "in": "$$kv.v"
                                    }
                                }
                            }
                        }}
                    ],
                    upsert=True
                ))

        if ops:
            res = col.bulk_write(ops, ordered=False)
            total_changed += res.upserted_count + res.modified_count
            print(f"{os.path.basename(path)} ({company}) -> {res.upserted_count + res.modified_count} upserted/updated")

    print("Total changed:", total_changed)

if __name__ == "__main__":
    ingest_folder()

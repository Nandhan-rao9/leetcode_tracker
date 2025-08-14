# companies_sync.py
import os, re, csv, glob, time, random, argparse, requests
from datetime import datetime, timezone
from typing import Optional, Tuple
from pymongo import MongoClient, UpdateOne
from dotenv import load_dotenv

# ------------------ Config ------------------
OWNER = "hxu296"
REPO = "leetcode-company-wise-problems-2022"
SUBDIR = "companies"        # folder in that repo
OUTDIR = "companies_csv"    # local folder

load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI") 
DB_NAME     = os.getenv("DB_NAME", "lc")
COLL_NAME   = os.getenv("COLLECTION", "problems_min")

if not MONGODB_URI:
    raise SystemExit("MONGODB_URI is not set. Put it in a .env next to this file or export it in the shell.")

# ------------------ Mongo -------------------
client = MongoClient(MONGODB_URI)
col = client[DB_NAME][COLL_NAME]

# ------------------ CSV helpers -------------
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
    # preserve words with capitals; title-case the rest
    return " ".join(w if any(c.isupper() for c in w) else w.title() for w in name.split())

# ------------------ Difficulty fetch --------
GQL_URL = "https://leetcode.com/graphql/"
GQL_QUERY = """
query questionData($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    difficulty
    topicTags { name }
  }
}
"""

def url_to_slug(url: str) -> Optional[str]:
    m = re.search(r"/problems/([^/]+)/?", url or "")
    return m.group(1) if m else None

def fetch_meta(slug: str, retries: int = 4) -> Tuple[Optional[str], list]:
    for attempt in range(retries + 1):
        try:
            r = requests.post(
                GQL_URL,
                json={"query": GQL_QUERY, "variables": {"titleSlug": slug}, "operationName": "questionData"},
                timeout=20,
                headers={"content-type": "application/json", "referer": "https://leetcode.com/"},
            )
            data = r.json()
            q = (data.get("data") or {}).get("question") or {}
            diff = q.get("difficulty")
            tags = [t["name"] for t in (q.get("topicTags") or [])]
            return diff, tags
        except Exception:
            if attempt == retries:
                return None, []
            time.sleep(0.6 * (2 ** attempt) + random.random() * 0.2)

# ------------------ Steps -------------------
def step_download_csvs():
    """Download all company CSVs to OUTDIR."""
    token = os.getenv("GITHUB_TOKEN")  # optional
    s = requests.Session()
    s.headers.update({
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    if token:
        s.headers["Authorization"] = f"Bearer {token}"

    os.makedirs(OUTDIR, exist_ok=True)
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{SUBDIR}"
    r = s.get(url, timeout=30)
    r.raise_for_status()
    items = r.json()

    csvs = [it for it in items if it.get("type") == "file" and it.get("name", "").lower().endswith(".csv")]
    print(f"Found {len(csvs)} CSVs in {SUBDIR}/")

    for it in csvs:
        name = it["name"]
        download_url = it["download_url"]
        data = s.get(download_url, timeout=60)
        data.raise_for_status()
        out_path = os.path.join(OUTDIR, name)
        with open(out_path, "wb") as f:
            f.write(data.content)
        print("Saved", out_path)

def step_ingest_csvs():
    """Ingest/merge CSVs so each doc has by_company, companies, num_occur."""
    # indexes (idempotent)
    col.create_index([("problem_link", 1)], unique=True)
    col.create_index([("problem_name", "text")])
    col.create_index([("companies", 1)])
    col.create_index([("num_occur", 1)])

    files = glob.glob(os.path.join(OUTDIR, "*.csv"))
    if not files:
        print("No CSVs found in", OUTDIR, "– run with --download first or put CSVs there.")
        return

    total_changed = 0
    for path in files:
        company = company_from_path(path)
        ops = []

        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                problem_name = pick(row, NAME_KEYS).strip()
                problem_link = pick(row, LINK_KEYS).strip()
                count        = to_int(pick(row, OCC_KEYS))
                if not problem_link or not problem_name:
                    continue

                company_obj = [{"k": company, "v": count}]

                # Update pipeline merges per-company counts and recomputes totals
                ops.append(UpdateOne(
                    {"problem_link": problem_link},
                    [
                        {"$set": {"problem_link": problem_link, "problem_name": problem_name}},
                        {"$set": {
                            "by_company": {
                                "$mergeObjects": [
                                    {"$ifNull": ["$by_company", {}]},
                                    {"$arrayToObject": [company_obj]}
                                ]
                            }
                        }},
                        {"$set": {
                            "companies": {
                                "$setUnion": [
                                    {"$ifNull": ["$companies", []]},
                                    [company]
                                ]
                            }
                        }},
                        {"$set": {
                            "num_occur": {
                                "$sum": {
                                    "$map": {
                                        "input": {"$objectToArray": {"$ifNull": ["$by_company", {}]}},
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
            changed = res.upserted_count + res.modified_count
            total_changed += changed
            print(f"{os.path.basename(path)} ({company}) -> {changed} upserted/updated")

    print("Total changed:", total_changed)

def step_backfill_meta(only_diff=False, limit=None, force=False):
    """Backfill difficulty (and tags unless only_diff) into this collection."""
    q_missing = (
        [{"difficulty": {"$exists": False}}, {"difficulty": None}]
        if only_diff else
        [{"difficulty": {"$exists": False}}, {"difficulty": None}, {"lcTags": {"$exists": False}}, {"lcTags": []}]
    )

    if force:
        cursor = col.find({}, {"_id": 1, "problem_link": 1}).limit(limit or 0)
        print("Force mode: updating all docs" + (f" (limit {limit})" if limit else ""))
    else:
        need = col.count_documents({"$or": q_missing})
        total = col.estimated_document_count()
        print(f"Total docs: {total}")
        print(f"Need update: {need}")
        if need == 0:
            print("Nothing to update (use --force to refresh anyway).")
            return
        cursor = col.find({"$or": q_missing}, {"_id": 1, "problem_link": 1}).limit(limit or 0)

    checked = updated = 0
    for doc in cursor:
        checked += 1
        slug = url_to_slug(doc.get("problem_link"))
        if not slug:
            continue

        diff, tags = fetch_meta(slug)
        set_fields = {"updatedAt": datetime.now(timezone.utc)}

        if diff:
            set_fields["difficulty"] = diff
        if not only_diff and tags:
            set_fields["lcTags"] = tags

        if len(set_fields) > 1:
            col.update_one({"_id": doc["_id"]}, {"$set": set_fields})
            updated += 1
            print(f"✔ {slug} -> {diff or '—'} {'(+tags)' if (not only_diff and tags) else ''}")
        else:
            print(f"… {slug}: no metadata")
        time.sleep(0.25 + random.random() * 0.15)

    print(f"Checked {checked}, updated {updated}.")

# ------------------ CLI ---------------------
def main():
    ap = argparse.ArgumentParser(description="Sync company CSVs → Mongo and (optionally) backfill difficulty/tags.")
    ap.add_argument("--download", action="store_true", help="Download all company CSVs from GitHub")
    ap.add_argument("--ingest",   action="store_true", help="Ingest/merge CSVs into Mongo")
    ap.add_argument("--backfill", action="store_true", help="Backfill difficulty + tags from LeetCode")
    ap.add_argument("--only-diff", action="store_true", help="Only backfill difficulty (skip lcTags)")
    ap.add_argument("--limit", type=int, default=None, help="Max docs to backfill")
    ap.add_argument("--force", action="store_true", help="Update meta even if fields already exist")
    args = ap.parse_args()

    print(f"Connecting: {MONGODB_URI}")
    print(f"Database:   {DB_NAME}")
    print(f"Collection: {COLL_NAME}")

    if args.download:
        step_download_csvs()
    if args.ingest:
        step_ingest_csvs()
    if args.backfill:
        step_backfill_meta(only_diff=args.only_diff, limit=args.limit, force=args.force)

    if not (args.download or args.ingest or args.backfill):
        # default: do all 3 in order
        step_download_csvs()
        step_ingest_csvs()
        step_backfill_meta(only_diff=False, limit=None, force=False)

if __name__ == "__main__":
    main()

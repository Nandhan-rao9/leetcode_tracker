import os, requests

OWNER = "hxu296"
REPO = "leetcode-company-wise-problems-2022"
SUBDIR = "companies"           # the folder we care about
OUTDIR = "companies_csv"
TOKEN = os.getenv("GITHUB_TOKEN")  # optional but recommended

session = requests.Session()
session.headers.update({
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
})
if TOKEN:
    session.headers["Authorization"] = f"Bearer {TOKEN}"

os.makedirs(OUTDIR, exist_ok=True)

url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{SUBDIR}"
r = session.get(url, timeout=30)
r.raise_for_status()
items = r.json()

csvs = [it for it in items if it.get("type") == "file" and it.get("name","").lower().endswith(".csv")]
print(f"Found {len(csvs)} CSVs in {SUBDIR}/")

for it in csvs:
    name = it["name"]
    download_url = it["download_url"]  # direct raw link from Contents API
    data = session.get(download_url, timeout=60)
    data.raise_for_status()
    out_path = os.path.join(OUTDIR, name)
    with open(out_path, "wb") as f:
        f.write(data.content)
    print("Saved", out_path)

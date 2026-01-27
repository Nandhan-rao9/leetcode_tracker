import requests
import os
import time
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from services.queries import USER_SUBMISSION_LIST_QUERY, GET_PROBLEMS_QUERY, QUESTION_TITLE_QUERY, FULL_SOLVED_LIST_QUERY

load_dotenv()

class LeetCodeClient:
    def __init__(self):
        self.session = requests.Session()
        self.url = "https://leetcode.com/graphql/"

        # Cookies
        self.session.cookies.set("LEETCODE_SESSION", os.getenv("LEETCODE_SESSION"), domain=".leetcode.com")
        self.session.cookies.set("csrftoken", os.getenv("LEETCODE_CSRF"), domain=".leetcode.com")

        # Headers
        self.headers = {
            "Content-Type": "application/json",
            "Referer": "https://leetcode.com",
            "Origin": "https://leetcode.com",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "x-csrftoken": os.getenv("LEETCODE_CSRF")
        }

        # Retry + backoff
        retry = Retry(
            total=5,
            backoff_factor=1.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"]
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retry))

    def fetch(self, query, variables):
        r = self.session.post(
            self.url,
            json={"query": query, "variables": variables},
            headers=self.headers,
            timeout=60
        )
        r.raise_for_status()
        return r.json()

    def fetch_all_accepted_slugs(self):
        """Fetches ALL 500+ solved slugs using the AC filter."""
        all_solved_slugs = [] # Initialize as empty list
        skip = 0
        limit = 100
        
        print("[LC] Starting deep scan for all solved problems...")

        while True:
            variables = {
                "categorySlug": "",
                "skip": skip,
                "limit": limit,
                "filters": {"status": "AC"} 
            }

            try:
                data = self.fetch(FULL_SOLVED_LIST_QUERY, variables)
                
                # Check if API returned data correctly
                if not data or "data" not in data or data["data"].get("problemsetQuestionList") is None:
                    print(f"[LC] API Error or Empty Response: {data}")
                    break
                
                questions = data["data"]["problemsetQuestionList"]["questions"]

                if not questions:
                    break
                
                for q in questions:
                    all_solved_slugs.append(q["titleSlug"])

                print(f"[LC] Retrieved {len(all_solved_slugs)} slugs...")
                
                if len(questions) < limit:
                    break
                
                skip += limit
                time.sleep(0.5)
                
            except Exception as e:
                print(f"[LC] Error during slug fetch: {e}")
                break
            
        return all_solved_slugs # ALWAYS returns a list, never None

    def fetch_titles_directly(self, slugs):
        """Converts slugs into clean titles."""
        results = []
        if not slugs:
            return results

        print(f"[LC] Hydrating titles for {len(slugs)} slugs...")
        for slug in slugs:
            try:
                data = self.fetch(QUESTION_TITLE_QUERY, {"titleSlug": slug})
                q = data["data"]["question"]
                if q:
                    results.append({"title": q["title"], "slug": q["titleSlug"]})
                time.sleep(0.15)
            except Exception:
                continue
        return results
    
    def fetch_titles_batch(self, slugs):
        """Fetches titles for a list of slugs in batches of 100."""
        results = []
        batch_size = 100
        slugs_list = list(slugs) # Ensure it's a list for slicing
        
        print(f"[LC] Batch hydrating titles for {len(slugs_list)} slugs...")

        for i in range(0, len(slugs_list), batch_size):
            batch = slugs_list[i:i + batch_size]
            
            # Use the global list query but filter specifically for these slugs
            variables = {
                "categorySlug": "",
                "skip": 0,
                "limit": batch_size,
                "filters": {"search": ",".join(batch)} 
            }

            try:
                data = self.fetch(GET_PROBLEMS_QUERY, variables)
                questions = data["data"]["problemsetQuestionList"]["questions"]
                
                for q in questions:
                    # Double check it's one of the slugs we asked for
                    if q["titleSlug"] in batch:
                        results.append({
                            "title": q["title"],
                            "slug": q["titleSlug"]
                        })
                
                print(f"[LC] Progress: {len(results)}/{len(slugs_list)} titles fetched...")
                time.sleep(0.5) # Gentle cooldown between batches
                
            except Exception as e:
                print(f"[LC] Batch fetch error: {e}")
                
        return results
import requests
import json
import os

# --- PASTE YOUR *NEW* COOKIES HERE ---
# Get these from your browser (Step 1)
LEETCODE_SESSION_COOKIE = "YOUR_TOKEN"
CSRF_TOKEN = "YOUR_TOKEN"
# ------------------------------------
# The URL for LeetCode's internal API
GRAPHQL_URL = "https://leetcode.com/graphql/"

# Setup your session cookies
cookies = {
    "LEETCODE_SESSION": LEETCODE_SESSION_COOKIE,
    "csrftoken": CSRF_TOKEN,
}

# Setup the headers
headers = {
    "Content-Type": "application/json",
    "Referer": "https://leetcode.com/",
    "Origin": "https://leetcode.com",
    "x-csrftoken": CSRF_TOKEN,
}

def get_problem_list():
    """
    Fetches the entire list of LeetCode problems, including their
    name, link (titleSlug), difficulty, and topic tags.
    This acts as our "lookup dictionary".
    """
    print("Fetching all problem data... (this may take a moment)")
    
    query = """
    query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
      problemsetQuestionList: questionList(
        categorySlug: $categorySlug
        limit: $limit
        skip: $skip
        filters: $filters
      ) {
        questions: data {
          title
          titleSlug  # This is used for the link
          difficulty # <-- We need this
          topicTags {
            name
            slug
          }
        }
      }
    }
    """
    
    variables = {
        "categorySlug": "",
        "skip": 0,
        "limit": -1,
        "filters": {}
    }
    
    payload = {
        "query": query,
        "variables": variables
    }

    try:
        response = requests.post(
            GRAPHQL_URL,
            json=payload,
            cookies=cookies,
            headers=headers
        )
        
        response.raise_for_status() 
        data = response.json()
        
        if 'errors' in data:
            print(f"\n❌ API returned an error: {data['errors']}")
            return

        output_filename = "all_leetcode_problems.json"
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            
        print(f"\n✅ Success! 'lookup dictionary' saved to '{os.path.abspath(output_filename)}'")
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ API Request Failed for Problem List: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response text: {e.response.text}")


def get_my_submissions():
    """
    Fetches ALL submissions for the user by paginating through the results.
    """
    print("\nFetching all your submissions... (this can take a while if you have many)")
    
    query = """
    query submissionList($offset: Int!, $limit: Int!, $lastKey: String, $questionSlug: String) {
      submissionList(
        offset: $offset
        limit: $limit
        lastKey: $lastKey
        questionSlug: $questionSlug
      ) {
        lastKey
        hasNext
        submissions {
          id
          title
          titleSlug
          statusDisplay
          lang
          timestamp
        }
      }
    }
    """
    
    limit = 20
    offset = 0
    current_key = None
    has_next_page = True
    all_submissions = []

    while has_next_page:
        variables = {
            "offset": offset,
            "limit": limit,
            "lastKey": current_key,
            "questionSlug": ""
        }
        
        payload = { "query": query, "variables": variables }
        print(f"Fetching batch (offset {offset})...")

        try:
            response = requests.post(
                GRAPHQL_URL,
                json=payload,
                cookies=cookies,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()

            if 'errors' in data:
                print(f"\n❌ API returned an error: {data['errors']}")
                break
                
            submission_data = data.get('data', {}).get('submissionList', {})
            submissions_batch = submission_data.get('submissions', [])
            
            if not submissions_batch:
                print("No more submissions found.")
                break

            all_submissions.extend(submissions_batch)
            
            has_next_page = submission_data.get('hasNext', False)
            current_key = submission_data.get('lastKey', None)
            offset += len(submissions_batch)

            print(f"Got {len(submissions_batch)} submissions. Total: {len(all_submissions)}. Has next: {has_next_page}")

            if not has_next_page:
                print("All submissions fetched.")
                break

        except requests.exceptions.RequestException as e:
            print(f"\n❌ API Request Failed during pagination: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response text: {e.response.text}")
                print("\n🚨 This error (400, 403, 500) almost always means your cookies are old or incorrect. Please get new cookies and try again.")
            break
            
    output_filename = "my_all_submissions.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(all_submissions, f, indent=2)
        
    print(f"\n✅ Success! Saved {len(all_submissions)} submissions to '{os.path.abspath(output_filename)}'")

# --- Main part of the script that runs ---
if __name__ == "__main__":
    print("Script started...")
    
    if "PASTE_YOUR" in LEETCODE_SESSION_COOKIE:
        print("🚨 ERROR: Please edit the script and paste your new cookie values at the top.")
    else:
        # 1. Get the master list of all problems
        print("--- Fetching Master Problem List ---")
        get_problem_list()
        
        # 2. Get all of your personal submissions
        print("\n--- Fetching Your Personal Submissions ---")
        get_my_submissions() 
        
    print("\nScript finished.")
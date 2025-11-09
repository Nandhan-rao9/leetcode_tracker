import json
import os
import datetime  # <-- ADDED THIS MODULE

def create_final_solved_list():
    """
    Reads the two JSON files and combines them to create a clean
    list of solved problems, including tags, links, difficulty,
    and the submission date.
    """
    print("Starting to process your files...")

    # --- 1. Load the Master Problem List ---
    try:
        with open("all_leetcode_problems.json", "r", encoding="utf-8") as f:
            all_problems_data = json.load(f)
        
        all_problems_list = all_problems_data.get('data', {}).get('problemsetQuestionList', {}).get('questions', [])
        if not all_problems_list:
            print("❌ Error: 'all_leetcode_problems.json' is empty or has the wrong format.")
            return
            
    except FileNotFoundError:
        print("❌ Error: 'all_leetcode_problems.json' not found.")
        print("Please run 'data.py' first.")
        return
    except json.JSONDecodeError:
        print("❌ Error: Could not read 'all_leetcode_problems.json'.")
        return

    # --- 2. Create a "Lookup Map" for fast access ---
    print(f"Loaded {len(all_problems_list)} problems into the lookup map.")
    problem_map = {
        problem['titleSlug']: problem 
        for problem in all_problems_list 
        if problem.get('titleSlug')
    }

    # --- 3. Load Your Submissions ---
    try:
        with open("my_all_submissions.json", "r", encoding="utf-8") as f:
            my_submissions = json.load(f)
            
        if not my_submissions:
            print("⚠️ Warning: 'my_all_submissions.json' is empty. Did you solve any problems?")
            
    except FileNotFoundError:
        print("❌ Error: 'my_all_submissions.json' not found.")
        print("Please run 'data.py' first.")
        return
    except json.JSONDecodeError:
        print("❌ Error: Could not read 'my_all_submissions.json'.")
        return

    # --- 4. Find Your "Accepted" Problems ---
    # The API returns submissions most-recent-first, so this loop
    # will find the *latest* accepted submission for each problem.
    solved_problems = {} # Use a dict to automatically handle duplicates
    
    for submission in my_submissions:
        if submission.get('statusDisplay') == "Accepted":
            slug = submission.get('titleSlug')
            
            # If this is the first time we're seeing this solved problem...
            if slug and slug not in solved_problems:
                problem_details = problem_map.get(slug)
                
                if problem_details:
                    # --- THIS IS THE NEW PART ---
                    # Get the Unix timestamp from the submission
                    unix_timestamp = submission.get('timestamp')
                    # Convert it to a human-readable string
                    submitted_date = datetime.datetime.fromtimestamp(
                        int(unix_timestamp)
                    ).strftime('%Y-%m-%d %H:%M:%S')
                    # --- END OF NEW PART ---

                    final_data = {
                        "title": problem_details.get('title'),
                        "difficulty": problem_details.get('difficulty'),
                        "link": f"https://leetcode.com/problems/{slug}/",
                        "submittedDate": submitted_date,  # <-- ADDED THE DATE
                        "topicTags": problem_details.get('topicTags', [])
                    }
                    solved_problems[slug] = final_data
                else:
                    print(f"Warning: Could not find details for solved problem: {slug}")

    # --- 5. Save the Final, Clean List ---
    final_list = list(solved_problems.values())
    
    output_filename = "my_solved_problems_final.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(final_list, f, indent=2)

    print("\n--- 🚀 SUCCESS! ---")
    print(f"Created '{output_filename}' with {len(final_list)} unique solved problems.")
    
    if final_list:
        print("\nHere is a sample of your first solved problem:")
        print(json.dumps(final_list[0], indent=2))

# --- Run the script ---
if __name__ == "__main__":
    create_final_solved_list()
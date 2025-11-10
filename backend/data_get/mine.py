import json
import os
import datetime  

def create_final_solved_list():
    """
    Creates a clean list of solved problems with titles, difficulty, topics, link, and submission date.
    """
    print("Starting to process your files...")

    # --- Load Master Problem List ---
    try:
        with open("all_leetcode_problems.json", "r", encoding="utf-8") as f:
            all_problems_data = json.load(f)
        all_problems_list = all_problems_data.get('data', {}).get('problemsetQuestionList', {}).get('questions', [])
        if not all_problems_list:
            print("❌ Error: 'all_leetcode_problems.json' is empty or malformed.")
            return
    except Exception as e:
        print(f"❌ Error loading problem list: {e}")
        return

    # Lookup map for quick slug access
    problem_map = {p['titleSlug']: p for p in all_problems_list if p.get('titleSlug')}
    print(f"Loaded {len(problem_map)} problems into the lookup map.")

    # --- Load Submissions ---
    try:
        with open("my_all_submissions.json", "r", encoding="utf-8") as f:
            my_submissions = json.load(f)
    except Exception as e:
        print(f"❌ Error loading submissions: {e}")
        return

    solved_problems = {}

    for submission in my_submissions:
        if submission.get('statusDisplay') == "Accepted":
            slug = submission.get('titleSlug')
            if not slug or slug in solved_problems:
                continue

            problem_details = problem_map.get(slug)
            if not problem_details:
                continue

            unix_timestamp = submission.get('timestamp')
            submitted_date = datetime.datetime.fromtimestamp(int(unix_timestamp)).strftime('%Y-%m-%d %H:%M:%S')

            solved_problems[slug] = {
                "title": problem_details.get('title'),
                "difficulty": problem_details.get('difficulty'),
                "link": f"https://leetcode.com/problems/{slug}/",
                "submittedDate": submitted_date,
                "topicTags": problem_details.get('topicTags', [])
            }

    final_list = list(solved_problems.values())
    output_filename = "my_solved_problems_final.json"

    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(final_list, f, indent=2)

    print(f"\n✅ SUCCESS! Saved {len(final_list)} solved problems → '{output_filename}'")

if __name__ == "__main__":
    create_final_solved_list()

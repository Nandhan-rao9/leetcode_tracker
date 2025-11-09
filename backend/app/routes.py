from flask import Flask, jsonify, request
from .db import solved_problems_collection
from bson import ObjectId # <-- IMPORTANT for Mongo
from collections import defaultdict
import random
from collections import defaultdict

def init_routes(app):
    
    @app.route('/api/problems/all', methods=['GET'])
    def get_all_solved_problems():
        """
        Fetches all solved problems from the database.
        """
        try:
            problems = list(solved_problems_collection.find({}))
            
            # We must convert the Mongo '_id' (ObjectId) to a string
            # so it can be sent as JSON.
            for problem in problems:
                problem['_id'] = str(problem['_id'])
                
            return jsonify({
                "success": True,
                "count": len(problems),
                "data": problems
            })
            
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
        
# ... inside backend/app/routes.py ...
    
    @app.route('/api/stats/topic-analysis', methods=['GET'])
    def get_topic_analysis():
        """
        [REFACTORED]
        Analyzes all solved problems to find topic counts,
        filtering out common/foundational topics.
        
        NOW reads from the simple 'all_topics' array.
        """
        
        # 1. Define your "blacklist"
        COMMON_TAGS_BLACKLIST = {
            "Array", "String", "Hash Table", "Math", 
            "Sorting", "Binary Search", "Simulation",
            "Data Structures"
        }

        try:
            problems = list(solved_problems_collection.find({}))
            topic_counts = defaultdict(lambda: {"count": 0, "solved": []})
            
            for problem in problems:
                problem_link = problem.get('link')
                problem_title = problem.get('title')
                
                # --- THIS IS THE NEW, CORRECT LOGIC ---
                # It iterates over your new 'all_topics' array
                for tag_name in problem.get('all_topics', []):
                # -------------------------------------
                    
                    if tag_name and tag_name not in COMMON_TAGS_BLACKLIST:
                        topic_counts[tag_name]["count"] += 1
                        topic_counts[tag_name]["solved"].append({
                            "title": problem_title,
                            "link": problem_link
                        })
                        
            # (Rest of the function is the same...)
            sorted_topics = []
            for name, data in topic_counts.items():
                sorted_topics.append({
                    "name": name, 
                    "count": data['count'],
                    "solved": data['solved']
                })
                
            sorted_topics.sort(key=lambda x: x['count'])
            
            return jsonify({
                "success": True,
                "count": len(sorted_topics),
                "data": sorted_topics
            })

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
        

    @app.route('/api/problems/find-similar', methods=['GET'])
    def find_similar_problems():
        """
        [REFACTORED]
        Finds 1 Easy, 1 Medium, and 1 Hard unsolved problem
        that is similar to the provided tags.
        Expects tags: /api/problems/find-similar?tags=Tree,Depth-First Search
        """
        try:
            # 1. Get tags from the query parameters
            query_tags = request.args.get('tags', '')
            if not query_tags:
                return jsonify({"success": False, "error": "No tags provided"}), 400
            
            # Convert string "Tag1,Tag2" into a set {'Tag1', 'Tag2'}
            topic_tags_set = set(query_tags.split(','))
            
            # 2. Get all SOLVED problem slugs from our database
            # (Your new schema uses the 'slug' field)
            solved_slugs = set()
            for problem in solved_problems_collection.find({}, {"slug": 1}):
                solved_slugs.add(problem['slug'])

            # 3. Find matching UNSOLVED problems and categorize
            similar_easy = []
            similar_medium = []
            similar_hard = []
            
            # 'all_problems_list' comes from your 'all_leetcode_problems.json'
            for problem in all_problems_list:
                # This file uses 'titleSlug', which is equivalent to your 'slug'
                problem_slug = problem['titleSlug'] 
                
                # Check if it's unsolved
                if problem_slug not in solved_slugs:
                    
                    # Get the tags from the 'all_problems_list'
                    problem_tags = set(tag['name'] for tag in problem.get('topicTags', []))
                    
                    # Find how many tags match
                    common_tags = topic_tags_set.intersection(problem_tags)
                    
                    # We'll define "similar" as having at least 1 common tag
                    if len(common_tags) > 0:
                        # Format the problem data
                        problem_data = {
                            "title": problem['title'],
                            "titleSlug": problem_slug, 
                            "difficulty": problem['difficulty'],
                            "link": f"https://leetcode.com/problems/{problem_slug}/"
                        }
                        
                        # Categorize by difficulty
                        if problem['difficulty'] == 'Easy':
                            similar_easy.append(problem_data)
                        elif problem['difficulty'] == 'Medium':
                            similar_medium.append(problem_data)
                        elif problem['difficulty'] == 'Hard':
                            similar_hard.append(problem_data)
            
            # 4. Shuffle each list and pick one
            final_list = []
            
            if similar_easy:
                random.shuffle(similar_easy)
                final_list.append(similar_easy[0])
            
            if similar_medium:
                random.shuffle(similar_medium)
                final_list.append(similar_medium[0])
                
            if similar_hard:
                random.shuffle(similar_hard)
                final_list.append(similar_hard[0])
            
            # final_list will now have 0-3 problems (1 of each difficulty)
            return jsonify({
                "success": True,
                "count": len(final_list),
                "data": final_list
            })

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
        
    @app.route('/api/stats/summary', methods=['GET'])
    def get_solved_summary():
        """
        Gets the total count of solved problems and the counts
        for Easy, Medium, and Hard.
        """
        try:
            # Use an aggregation pipeline to count by difficulty
            pipeline = [
                {
                    "$group": {
                        "_id": "$difficulty", # Group by the difficulty field
                        "count": { "$sum": 1 } # Count 1 for each document
                    }
                }
            ]
            results = list(solved_problems_collection.aggregate(pipeline))
            
            summary = {
                "Easy": 0,
                "Medium": 0,
                "Hard": 0,
                "total": 0
            }
            
            # Process the aggregation results
            for item in results:
                difficulty = item.get("_id") # This will be "Easy", "Medium", or "Hard"
                count = item.get("count", 0)
                if difficulty in summary:
                    summary[difficulty] = count
                summary["total"] += count
                
            return jsonify({
                "success": True,
                "data": summary
            })

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
        
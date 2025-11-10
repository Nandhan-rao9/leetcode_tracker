from flask import Flask, jsonify, request
from .db import solved_problems_collection, unsolved_problems_collection # Added unsolved_problems_collection
from bson import ObjectId # <-- IMPORTANT for Mongo
from collections import defaultdict
import random
# Removed duplicate defaultdict import

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
        
    
    # This route was incorrectly unindented in the prompt.
    # It has been moved inside the init_routes function.
    @app.route('/api/problems/find-similar', methods=['GET'])
    def find_similar_problems():
        """
        Finds 1 Easy, 1 Medium, and 1 Hard unsolved problem by
        querying the 'unsolved_problems' collection directly.
        Now supports case-insensitive matching and fallback logic.
        """
        try:
            query_tags = request.args.get('tags', '')
            if not query_tags:
                return jsonify({"success": False, "error": "No tags provided"}), 400

            # Normalize input tags (lowercase, strip spaces)
            topic_tags_list = [t.lower().strip() for t in query_tags.split(',') if t.strip()]
            if not topic_tags_list:
                return jsonify({"success": False, "error": "No valid tags provided"}), 400

            # Case-insensitive queries using lowercase all_topics
            easy_query = {
                "difficulty": "Easy",
                "all_topics": {"$in": topic_tags_list}
            }
            medium_query = {
                "difficulty": "Medium",
                "all_topics": {"$in": topic_tags_list}
            }
            hard_query = {
                "difficulty": "Hard",
                "all_topics": {"$in": topic_tags_list}
            }

            # Find matches
            similar_easy = list(unsolved_problems_collection.find(easy_query))
            similar_medium = list(unsolved_problems_collection.find(medium_query))
            similar_hard = list(unsolved_problems_collection.find(hard_query))

            final_list = []

            # random is imported at the top of the file
            if similar_easy:
                random.shuffle(similar_easy)
                final_list.append(similar_easy[0])
            if similar_medium:
                random.shuffle(similar_medium)
                final_list.append(similar_medium[0])
            if similar_hard:
                random.shuffle(similar_hard)
                final_list.append(similar_hard[0])

            # --- NEW FALLBACK LOGIC ---
            if not final_list:
                # Try broader match: any difficulty
                fallback = list(unsolved_problems_collection.find({
                    "all_topics": {"$in": topic_tags_list}
                }).limit(3))
                if fallback:
                    random.shuffle(fallback)
                    final_list = fallback
            # ---------------------------

            # Convert ObjectIds to strings
            for p in final_list:
                p["_id"] = str(p["_id"])

            return jsonify({
                "success": True,
                "count": len(final_list),
                "data": final_list
            })

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
        
    @app.route('/api/problems/generate-set', methods=['POST'])
    def generate_practice_set():
        """
        [NEW]
        Generates a custom practice set based on user criteria.
        Expects a JSON body like:
        {
            "topics": ["Array", "Dynamic Programming"],
            "revision_count": 2,
            "new_count": 3
        }
        """
        try:
            data = request.get_json()
            topic_list = data.get('topics', [])
            revision_count = data.get('revision_count', 0)
            new_count = data.get('new_count', 0)

            if not topic_list:
                return jsonify({"success": False, "error": "No topics selected"}), 400
            
            # --- 1. Get REVISION problems (from SOLVED) ---
            revision_problems = []
            if revision_count > 0:
                # Find solved problems where 'all_topics' overlaps with the 'topic_list'
                query = {"all_topics": {"$in": topic_list}}
                
                # Use $sample (a fast, random Mongo aggregation)
                pipeline = [
                    {"$match": query},
                    {"$sample": {"size": revision_count}}
                ]
                revision_problems = list(solved_problems_collection.aggregate(pipeline))

            # --- 2. Get NEW problems (from UNSOLVED) ---
            new_problems = []
            if new_count > 0:
                # Find unsolved problems
                query = {"all_topics": {"$in": topic_list}}
                pipeline = [
                    {"$match": query},
                    {"$sample": {"size": new_count}}
                ]
                new_problems = list(unsolved_problems_collection.aggregate(pipeline))
            
            # --- 3. Combine and clean the final list ---
            final_list = revision_problems + new_problems
            
            # Add a 'type' flag for the frontend and clean _id
            for problem in final_list:
                problem['_id'] = str(problem['_id'])
                # Check if the problem exists in the 'new_problems' list
                if any(p['_id'] == problem['_id'] for p in new_problems):
                    problem['type'] = 'New'
                else:
                    problem['type'] = 'Revision'
            
            # Shuffle the final list so new/revision are mixed
            random.shuffle(final_list)

            return jsonify({
                "success": True,
                "data": final_list
            })

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
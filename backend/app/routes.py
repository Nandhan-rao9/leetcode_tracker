from flask import Flask, jsonify, request
from .db import solved_problems_collection
from bson import ObjectId # <-- IMPORTANT for Mongo
from collections import defaultdict
import random

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
        

    @app.route('/api/stats/topic-analysis', methods=['GET'])
    def get_topic_analysis():
        """
        Analyzes all solved problems to find topic counts,
        filtering out common/foundational topics.
        """
        
        # 1. Define your "blacklist" of common tags to ignore
        # We can add more to this list later
        COMMON_TAGS_BLACKLIST = {
            "Array", "String", "Hash Table", "Math", 
            "Sorting", "Binary Search", "Simulation",
            "Data Structures" # A custom tag from LeetCode
        }

        try:
            # 2. Get all problems from the database
            problems = list(solved_problems_collection.find({}))
            
            # 3. Count all topics
            # defaultdict is great for this!
            topic_counts = defaultdict(int)
            
            for problem in problems:
                for tag in problem.get('topicTags', []):
                    tag_name = tag.get('name')
                    
                    # 4. Only count if it's NOT in our blacklist
                    if tag_name and tag_name not in COMMON_TAGS_BLACKLIST:
                        topic_counts[tag_name] += 1
                        
            # 5. Convert the dictionary to a sorted list
            # We sort by count (lowest first) to find weaknesses
            sorted_topics = []
            for name, count in topic_counts.items():
                sorted_topics.append({"name": name, "count": count})
                
            # Sort by count, ascending
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
        Finds 3 similar problems based on topic tags.
        Expects a comma-separated list of tags in a query param
        e.g., /api/problems/find-similar?tags=Tree,Depth-First Search
        """
        try:
            # 1. Get tags from the query parameters (e.g., "Tree,DFS")
            query_tags = request.args.get('tags', '')
            if not query_tags:
                return jsonify({"success": False, "error": "No tags provided"}), 400
            
            # Convert string "Tag1,Tag2" into a set {'Tag1', 'Tag2'}
            topic_tags_set = set(query_tags.split(','))
            
            # 2. Get all SOLVED problem slugs from our database
            solved_slugs = set()
            for problem in solved_problems_collection.find({}, {"titleSlug": 1}):
                solved_slugs.add(problem['titleSlug'])

            # 3. Find matching UNSOLVED problems from our big list
            similar_problems = []
            for problem in all_problems_list:
                # Check if it's unsolved and Medium/Hard
                if problem['titleSlug'] not in solved_slugs and (problem['difficulty'] == 'Medium' or problem['difficulty'] == 'Hard'):
                    
                    problem_tags = set(tag['name'] for tag in problem.get('topicTags', []))
                    
                    # Find how many tags match
                    common_tags = topic_tags_set.intersection(problem_tags)
                    
                    # We'll define "similar" as having at least 1 common tag
                    if len(common_tags) > 0:
                        similar_problems.append({
                            "title": problem['title'],
                            "titleSlug": problem['titleSlug'],
                            "difficulty": problem['difficulty'],
                            "link": f"https://leetcode.com/problems/{problem['titleSlug']}/"
                        })
            
            # 4. Shuffle and pick 3
            random.shuffle(similar_problems)
            final_list = similar_problems[:3]
            
            return jsonify({
                "success": True,
                "count": len(final_list),
                "data": final_list
            })

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    # We will add more routes here later (e.g., /api/stats, /api/generate-set)
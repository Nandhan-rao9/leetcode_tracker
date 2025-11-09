from flask import Flask, jsonify
from .db import solved_problems_collection
from bson import ObjectId # <-- IMPORTANT for Mongo

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

    # We will add more routes here later (e.g., /api/stats, /api/generate-set)
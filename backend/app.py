# backend/app.py
from flask import Flask, jsonify
from flask_cors import CORS
from routes.summary import summary_bp
from routes.companies import companies_bp
from routes.problems import problems_bp

app = Flask(__name__)
CORS(app)  # allow frontend at localhost:3000 to call API

# register blueprints
app.register_blueprint(summary_bp)
app.register_blueprint(companies_bp)
app.register_blueprint(problems_bp)

@app.route("/")
def home():
    return jsonify({"status": "ok", "message": "LeetBuddy API running"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)

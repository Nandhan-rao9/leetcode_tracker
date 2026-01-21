from flask import Flask
from flask_cors import CORS

from routes.summary import summary_bp
from routes.companies import companies_bp
from routes.problems import problems_bp

app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": "*"}})

app.register_blueprint(summary_bp)
app.register_blueprint(companies_bp)
app.register_blueprint(problems_bp)

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000, debug=True)

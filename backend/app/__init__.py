from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    
    # Enable CORS (Cross-Origin Resource Sharing)
    # This allows your React frontend (on localhost:3000)
    # to make requests to your Flask backend (on localhost:5000)
    CORS(app)

    # Import and register your routes
    with app.app_context():
        from . import routes
        routes.init_routes(app)

    return app
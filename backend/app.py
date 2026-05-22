from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

from routes.auth import auth_bp
from routes.summary import summary_bp
from routes.companies import companies_bp
from routes.problems import problems_bp
from utils.errors import register_error_handlers
from utils.db import create_indexes

app = Flask(__name__)

# CORS configuration - restrict origins for security
allowed_origins = os.getenv("FRONTEND_URL", "http://localhost:3000,http://localhost:3005").split(",")
CORS(
    app,
    resources={r"/api/*": {"origins": allowed_origins}},
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["Content-Type", "Authorization"]
)

# Rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Apply stricter limits to auth endpoints
@limiter.limit("5 per minute")
def auth_rate_limit():
    pass

# Register error handlers
register_error_handlers(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(summary_bp)
app.register_blueprint(companies_bp)
app.register_blueprint(problems_bp)

# Create database indexes on startup
with app.app_context():
    create_indexes()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

from functools import wraps
from flask import request, jsonify, g
import jwt
import os

def require_auth(f):
    """Decorator to protect routes with JWT authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get("Authorization")

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"error": "Missing authentication token"}), 401

        try:
            secret_key = os.getenv("JWT_SECRET_KEY")
            if not secret_key:
                return jsonify({"error": "Server configuration error"}), 500

            payload = jwt.decode(token, secret_key, algorithms=["HS256"])
            g.user_id = payload["user_id"]
            g.user_email = payload["email"]

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        except Exception as e:
            return jsonify({"error": "Authentication failed"}), 401

        return f(*args, **kwargs)

    return decorated

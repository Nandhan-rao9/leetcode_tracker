from flask import Blueprint, request, jsonify, g, make_response
from utils.db import users_col
from utils.validation import validate_email, validate_password, validate_username
from utils.crypto import encrypt_credential
from utils.errors import APIError
from middleware.auth import require_auth
import bcrypt
import jwt
import time
import os
from bson import ObjectId

auth_bp = Blueprint("auth", __name__)

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY")
ACCESS_TOKEN_EXPIRY = 900  # 15 minutes
REFRESH_TOKEN_EXPIRY = 604800  # 7 days

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode(), password_hash.encode())

def create_access_token(user_id: str, email: str) -> str:
    """Create a JWT access token."""
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": int(time.time()) + ACCESS_TOKEN_EXPIRY,
        "type": "access"
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")

def create_refresh_token(user_id: str) -> str:
    """Create a JWT refresh token."""
    payload = {
        "user_id": user_id,
        "exp": int(time.time()) + REFRESH_TOKEN_EXPIRY,
        "type": "refresh"
    }
    return jwt.encode(payload, JWT_REFRESH_SECRET_KEY, algorithm="HS256")

def decode_refresh_token(token: str) -> dict:
    """Decode a refresh token."""
    return jwt.decode(token, JWT_REFRESH_SECRET_KEY, algorithms=["HS256"])


@auth_bp.route("/api/auth/register", methods=["POST"])
def register():
    """Register a new user."""
    try:
        data = request.get_json()

        if not data:
            raise APIError("Request body is required", 400)

        email = data.get("email", "").strip()
        password = data.get("password", "")
        username = data.get("username", "").strip()

        # Validate inputs
        valid, error = validate_email(email)
        if not valid:
            raise APIError(error, 400)

        valid, error = validate_password(password)
        if not valid:
            raise APIError(error, 400)

        valid, error = validate_username(username)
        if not valid:
            raise APIError(error, 400)

        # Check if email already exists
        if users_col.find_one({"email": email}):
            raise APIError("Email already registered", 400)

        # Check if username already exists
        if users_col.find_one({"username": username}):
            raise APIError("Username already taken", 400)

        # Optional LeetCode credentials
        leetcode_username = data.get("leetcode_username", "").strip()
        leetcode_session = data.get("leetcode_session", "").strip()
        leetcode_csrf = data.get("leetcode_csrf", "").strip()

        # Create user document
        user_doc = {
            "email": email,
            "password_hash": hash_password(password),
            "username": username,
            "leetcode_username": leetcode_username if leetcode_username else None,
            "leetcode_session_encrypted": encrypt_credential(leetcode_session) if leetcode_session else None,
            "leetcode_csrf_encrypted": encrypt_credential(leetcode_csrf) if leetcode_csrf else None,
            "ingestion_status": "ready",
            "last_ingested_at": None,
            "created_at": time.time(),
            "updated_at": time.time()
        }

        result = users_col.insert_one(user_doc)

        return jsonify({
            "message": "User registered successfully",
            "user_id": str(result.inserted_id)
        }), 201

    except APIError as e:
        raise e
    except Exception as e:
        raise APIError(f"Registration failed: {str(e)}", 500)


@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    """Login a user and return tokens."""
    try:
        data = request.get_json()

        if not data:
            raise APIError("Request body is required", 400)

        email = data.get("email", "").strip()
        password = data.get("password", "")

        if not email or not password:
            raise APIError("Email and password are required", 400)

        # Find user
        user = users_col.find_one({"email": email})

        if not user or not verify_password(password, user["password_hash"]):
            raise APIError("Invalid email or password", 401)

        # Create tokens
        user_id = str(user["_id"])
        access_token = create_access_token(user_id, user["email"])
        refresh_token = create_refresh_token(user_id)

        # Create response with refresh token in httpOnly cookie
        response = make_response(jsonify({
            "message": "Login successful",
            "accessToken": access_token,
            "user": {
                "id": user_id,
                "email": user["email"],
                "username": user["username"]
            }
        }))

        # Set refresh token as httpOnly cookie
        response.set_cookie(
            "refresh_token",
            refresh_token,
            httponly=True,
            secure=os.getenv("FLASK_ENV") == "production",  # HTTPS only in production
            samesite="Lax",
            max_age=REFRESH_TOKEN_EXPIRY
        )

        return response, 200

    except APIError as e:
        raise e
    except Exception as e:
        raise APIError(f"Login failed: {str(e)}", 500)


@auth_bp.route("/api/auth/refresh", methods=["POST"])
def refresh():
    """Refresh access token using refresh token."""
    try:
        refresh_token = request.cookies.get("refresh_token")

        if not refresh_token:
            raise APIError("Refresh token missing", 401)

        # Decode refresh token
        try:
            payload = decode_refresh_token(refresh_token)
            user_id = payload["user_id"]
        except jwt.ExpiredSignatureError:
            raise APIError("Refresh token expired", 401)
        except jwt.InvalidTokenError:
            raise APIError("Invalid refresh token", 401)

        # Get user from database
        user = users_col.find_one({"_id": ObjectId(user_id)})

        if not user:
            raise APIError("User not found", 404)

        # Create new access token
        access_token = create_access_token(str(user["_id"]), user["email"])

        return jsonify({
            "accessToken": access_token
        }), 200

    except APIError as e:
        raise e
    except Exception as e:
        raise APIError(f"Token refresh failed: {str(e)}", 500)


@auth_bp.route("/api/auth/logout", methods=["POST"])
def logout():
    """Logout user by clearing refresh token cookie."""
    response = make_response(jsonify({"message": "Logout successful"}))
    response.set_cookie("refresh_token", "", expires=0)
    return response, 200


@auth_bp.route("/api/auth/me", methods=["GET"])
@require_auth
def get_current_user():
    """Get current authenticated user profile."""
    try:
        user = users_col.find_one({"_id": ObjectId(g.user_id)})

        if not user:
            raise APIError("User not found", 404)

        return jsonify({
            "id": str(user["_id"]),
            "email": user["email"],
            "username": user["username"],
            "leetcode_username": user.get("leetcode_username"),
            "ingestion_status": user.get("ingestion_status"),
            "last_ingested_at": user.get("last_ingested_at"),
            "created_at": user.get("created_at")
        }), 200

    except APIError as e:
        raise e
    except Exception as e:
        raise APIError(f"Failed to fetch user: {str(e)}", 500)

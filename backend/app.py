import os
from datetime import timedelta

from flask import Flask, request, jsonify, Blueprint
from flask_jwt_extended import JWTManager, create_access_token
from werkzeug.security import generate_password_hash, check_password_hash

# Temporary in-memory store (placeholder until DB integration)
users = []

# -------------------------
# Auth blueprint + routes
# -------------------------

auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


def _get_env(name: str) -> str:
    """
    Safely fetch required environment variables.

    Kept outside create_app() to keep its cognitive complexity low.
    """
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Required environment variable '{name}' is missing.")
    return value


@auth_bp.route("/signup", methods=["POST"])
def signup():
    """
    User registration with validation, hashing, and controlled admin creation.

    Response contract (what your tests expect):
    - 201 on success
    {
      "message": "User registered",
      "user": { ...no password_hash... },
      "access_token": "<jwt>"
    }
    """
    data = request.get_json(silent=True) or {}

    required = ["email", "first_name", "last_name", "password", "address"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return (
            jsonify(
                {"error": "Missing required fields", "missing_fields": missing}
            ),
            400,
        )

    email = data["email"].strip().lower()
    if any(u["email"] == email for u in users):
        return jsonify({"error": "User already exists"}), 400

    # Admin creation guard using an env-based secret code
    is_admin = False
    admin_code = data.get("admin_code")
    expected_code = os.environ.get("ADMIN_SIGNUP_CODE")

    if admin_code and expected_code and admin_code == expected_code:
        is_admin = True

    user = {
        "id": len(users) + 1,
        "email": email,
        "first_name": data["first_name"].strip(),
        "last_name": data["last_name"].strip(),
        "address": data["address"].strip(),
        "password_hash": generate_password_hash(
            data["password"], method="pbkdf2:sha256"
        ),
        "is_admin": is_admin,
    }
    users.append(user)

    # Response must not expose password_hash
    user_response = {k: v for k, v in user.items() if k != "password_hash"}

    # Issue token on signup (tests expect access_token in signup response)
    access_token = create_access_token(
        identity={"id": user["id"], "is_admin": user["is_admin"]}
    )

    return (
        jsonify(
            {
                "message": "User registered",
                "user": user_response,
                "access_token": access_token,
            }
        ),
        201,
    )


@auth_bp.route("/signin", methods=["POST"])
def signin():
    """
    Authenticate user and return JWT + user payload.

    Response contract (what your tests expect):
    - 200 on success
    {
      "message": "Signin successful",
      "access_token": "<jwt>",
      "user": { ...no password_hash... }
    }
    """
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = next((u for u in users if u["email"] == email), None)
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid email or password"}), 400

    access_token = create_access_token(
        identity={"id": user["id"], "is_admin": user["is_admin"]}
    )
    user_response = {k: v for k, v in user.items() if k != "password_hash"}

    return (
        jsonify(
            {
                "message": "Signin successful",
                "access_token": access_token,
                "user": user_response,
            }
        ),
        200,
    )


def create_app() -> Flask:
    """
    Application factory for the AutoMart backend.

    Kept intentionally simple to satisfy Sonar's cognitive complexity rules.
    """
    app = Flask(__name__)

    # --- Configuration ---
    app.config["JWT_SECRET_KEY"] = _get_env("JWT_SECRET_KEY")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=12)
    app.config.setdefault("TESTING", False)

    # Initialize JWT extension (no unused local variable)
    JWTManager(app)

    # Health check / root endpoint
    @app.get("/")
    def home():
        return jsonify({"message": "AutoMart API v1 running"}), 200

    # Register blueprints
    app.register_blueprint(auth_bp)

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(debug=True)

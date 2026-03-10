import os
from datetime import timedelta

from flask import Flask, request, jsonify, Blueprint
from flask_jwt_extended import JWTManager, create_access_token
from werkzeug.security import generate_password_hash, check_password_hash

# Temporary in-memory store (will be replaced by a real DB later)
users = []

# --- Blueprint setup ---


auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


def _get_jwt_secret() -> str:
    """
    Retrieve the JWT secret from the environment.

    Extracted into a helper to reduce cognitive complexity inside create_app().
    """
    try:
        return os.environ["JWT_SECRET_KEY"]
    except KeyError as exc:
        raise RuntimeError(
            "JWT_SECRET_KEY environment variable must be set (no hard-coded secrets)."
        ) from exc


@auth_bp.route("/signup", methods=["POST"])
def signup():
    """
    Register a new user.

    Expected JSON body:
    {
      "email": "you@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "password": "plaintext",
      "address": "Kampala",
      // optional:
      "admin_code": "some-secret-code"
    }

    Notes:
    - We do NOT trust a client-side `is_admin` flag.
    - Admin creation is controlled via ADMIN_SIGNUP_CODE env var.
    """
    data = request.get_json(silent=True) or {}

    required_fields = [
        "email",
        "first_name",
        "last_name",
        "password",
        "address",
    ]
    missing = [f for f in required_fields if not data.get(f)]
    if missing:
        return (
            jsonify(
                {
                    "error": "Missing required fields",
                    "missing_fields": missing,
                }
            ),
            400,
        )

    email = data["email"].strip().lower()

    # Check for duplicate email
    if any(u["email"] == email for u in users):
        return jsonify({"error": "User already exists"}), 400

    # Admin creation is guarded by an env-based secret code
    is_admin = False
    admin_code = data.get("admin_code")
    expected_admin_code = os.environ.get("ADMIN_SIGNUP_CODE")

    if admin_code and expected_admin_code and admin_code == expected_admin_code:
        is_admin = True

    user_id = len(users) + 1

    user = {
        "uuid": f"user_{user_id}",
        "id": user_id,
        "email": email,
        "first_name": data["first_name"].strip(),
        "last_name": data["last_name"].strip(),
        "address": data["address"].strip(),
        "is_admin": is_admin,
        # Store only hashed password (PBKDF2, not raw SHA/scrypt)
        "password_hash": generate_password_hash(
            data["password"],
            method="pbkdf2:sha256",
        ),
    }

    users.append(user)

    # Issue token on signup
    access_token = create_access_token(
        identity={"id": user["id"], "is_admin": user["is_admin"]}
    )

    response_payload = {
        "message": "User registered",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "address": user["address"],
            "is_admin": user["is_admin"],
        },
        "access_token": access_token,
    }
    return jsonify(response_payload), 201


@auth_bp.route("/signin", methods=["POST"])
def signin():
    """
    Sign in an existing user.

    Expected JSON body:
    {
      "email": "goats@gmail.com",
      "password": "plaintext"
    }
    """
    data = request.get_json(silent=True) or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = next((u for u in users if u["email"] == email), None)

    if not user or not check_password_hash(user["password_hash"], password):
        # Generic message to avoid leaking which field is wrong
        return jsonify({"error": "Invalid email or password"}), 400

    access_token = create_access_token(
        identity={"id": user["id"], "is_admin": user["is_admin"]}
    )

    return (
        jsonify(
            {
                "message": "Signin successful",
                "access_token": access_token,
                "user": {
                    "id": user["id"],
                    "email": user["email"],
                    "first_name": user["first_name"],
                    "last_name": user["last_name"],
                    "address": user["address"],
                    "is_admin": user["is_admin"],
                },
            }
        ),
        200,
    )


def create_app() -> Flask:
    """
    Application factory for the AutoMart backend.

    Using a factory pattern allows:
    - Multiple app instances (testing, dev, prod)
    - Config injection
    - Cleaner separation into blueprints later
    """
    app = Flask(__name__)

    # --- Configuration ---
    jwt_secret = _get_jwt_secret()
    app.config["JWT_SECRET_KEY"] = jwt_secret
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)
    app.config.setdefault("TESTING", False)

    # Initialize JWT extension (no need to store in a local variable)
    JWTManager(app)

    @app.route("/")
    def home():
        """
        Simple health check for the API.
        """
        return jsonify({"message": "AutoMart API v1 running"}), 200

    # Register blueprints
    app.register_blueprint(auth_bp)

    return app


if __name__ == "__main__":
    application = create_app()
    isinstance(application, Flask)  # sanity check for type hinting ass
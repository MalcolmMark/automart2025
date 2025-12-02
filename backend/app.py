import os
import hashlib
from datetime import timedelta

from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token

# Temporary in-memory store (will be replaced by a real DB later)
users = []


def hash_password(password: str) -> str:
    """Hash a password using SHA-256 (demo-grade, not for production)."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(stored_hash: str, password: str) -> bool:
    """Check a plaintext password against the stored SHA-256 hash."""
    return stored_hash == hash_password(password)


def create_app() -> Flask:
    """
    Minimal application factory.

    This lets us scale into a more modular structure (blueprints, configs, etc.)
    without rewriting everything later.
    """
    app = Flask(__name__)

    # --- Configuration ---
    app.config["JWT_SECRET_KEY"] = os.environ.get(
        "JWT_SECRET_KEY",
        "dev-super-secret-key-change-me",
    )
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)

    # Testing flag can be overridden in tests
    app.config.setdefault("TESTING", False)

    jwt = JWTManager(app)  # noqa: F841

    # --- Routes ---

    @app.route("/")
    def home():
        return jsonify({"message": "AutoMart API v1 running"}), 200

    @app.route("/api/v1/auth/signup", methods=["POST"])
    def signup():
        """
        Expected JSON body (aligns with your signup UI):
        {
          "email": "you@example.com",
          "first_name": "John",
          "last_name": "Doe",
          "password": "plaintext",
          "address": "Kampala",
          "is_admin": false | true  # or "false"/"true" from HTML form
        }
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

        # Normalise is_admin to bool
        raw_is_admin = data.get("is_admin", False)
        if isinstance(raw_is_admin, str):
            is_admin = raw_is_admin.strip().lower() == "true"
        else:
            is_admin = bool(raw_is_admin)

        # Check for duplicate email
        if any(u["email"].lower() == data["email"].lower() for u in users):
            return jsonify({"error": "User already exists"}), 400

        user_id = len(users) + 1

        user = {
            "id": user_id,
            "email": data["email"].lower(),
            "first_name": data["first_name"].strip(),
            "last_name": data["last_name"].strip(),
            "address": data["address"].strip(),
            "is_admin": is_admin,
            # Store only SHA-256 hash
            "password_hash": hash_password(data["password"]),
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

    @app.route("/api/v1/auth/signin", methods=["POST"])
    def signin():
        """
        Expected JSON body:
        {
          "email": "you@example.com",
          "password": "plaintext"
        }
        """
        data = request.get_json(silent=True) or {}

        email = data.get("email", "").lower()
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        user = next((u for u in users if u["email"] == email), None)

        if not user or not verify_password(user["password_hash"], password):
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

    return app


# Allow `python app.py` for local dev
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

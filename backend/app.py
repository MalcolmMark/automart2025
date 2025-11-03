from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token
from datetime import timedelta

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "supersecretkey"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)
jwt = JWTManager(app)

users = []  # temporary in-memory store


@app.route("/")
def home():
    return jsonify({"message": "AutoMart API v1 running"}), 200


@app.route("/api/v1/auth/signup", methods=["POST"])
def signup():
    data = request.json
    if any(u["email"] == data["email"] for u in users):
        return jsonify({"error": "User already exists"}), 400
    user = {
        "id": len(users) + 1,
        "email": data["email"],
        "password": data["password"],
    }
    users.append(user)
    return jsonify({"message": "User registered", "user": user}), 201


@app.route("/api/v1/auth/signin", methods=["POST"])
def signin():
    data = request.json
    user = next(
        (u for u in users if u["email"] == data["email"] and u["password"] == data["password"]),
        None,
    )
    if not user:
        return jsonify({"error": "Invalid login"}), 400
    token = create_access_token(identity=user["id"])
    return jsonify({"access_token": token}), 200


if __name__ == "__main__":
    app.run(debug=True)

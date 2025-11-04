from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta

app = Flask(__name__)

# JWT config
app.config["JWT_SECRET_KEY"] = "supersecretkey"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)
jwt = JWTManager(app)

# In-memory stores (simple for Challenge 2)
users = []   # [{id,email,password,is_admin?}]
cars = []    # [{id, owner, manufacturer, model, price, state, status, body_type, description}]
orders = []  # keep for later steps
flags = []   # keep for later steps


@app.route("/")
def home():
    return jsonify({"message": "AutoMart API v1 running"}), 200


# ---------- AUTH ----------
@app.route("/api/v1/auth/signup", methods=["POST"])
def signup():
    data = request.get_json() or {}
    if not data.get("email") or not data.get("password"):
        return jsonify({"error": "email and password required"}), 400

    if any(u["email"] == data["email"] for u in users):
        return jsonify({"error": "User already exists"}), 400

    user = {
        "id": len(users) + 1,
        "email": data["email"],
        "password": data["password"],  # NOTE: plaintext for demo; hash later
        "is_admin": bool(data.get("is_admin", False)),
    }
    users.append(user)
    return jsonify({"status": "success", "data": {"id": user["id"], "email": user["email"]}}), 201


@app.route("/api/v1/auth/signin", methods=["POST"])
def signin():
    data = request.get_json() or {}
    user = next(
        (u for u in users if u["email"] == data.get("email") and u["password"] == data.get("password")),
        None,
    )
    if not user:
        return jsonify({"error": "Invalid login"}), 400

    token = create_access_token(identity=user["id"])
    return jsonify({"status": "success", "data": {"token": token, "id": user["id"]}}), 200


# ---------- CARS ----------
def find_car(car_id: int):
    return next((c for c in cars if c["id"] == car_id), None)


@app.route("/api/v1/car", methods=["POST"])
@jwt_required()
def create_car():
    """Create a car ad (owner = current user)."""
    uid = get_jwt_identity()
    data = request.get_json() or {}

    required = ["manufacturer", "model", "price", "state", "body_type"]
    missing = [k for k in required if k not in data]
    if missing:
        return jsonify({"error": f"Missing: {', '.join(missing)}"}), 400

    car = {
        "id": len(cars) + 1,
        "owner": uid,
        "manufacturer": data["manufacturer"],
        "model": data["model"],
        "price": float(data["price"]),
        "state": data["state"],              # "new" | "used"
        "status": "available",               # default
        "body_type": data["body_type"],      # e.g., sedan/suv
        "description": data.get("description", "")
    }
    cars.append(car)
    return jsonify({"status": "success", "data": car}), 201


@app.route("/api/v1/car/<int:car_id>/price", methods=["PATCH"])
@jwt_required()
def update_price(car_id):
    """Owner updates price of his/her car."""
    uid = get_jwt_identity()
    car = find_car(car_id)
    if not car:
        return jsonify({"error": "Car not found"}), 404
    if car["owner"] != uid:
        return jsonify({"error": "Forbidden"}), 403

    data = request.get_json() or {}
    if "price" not in data:
        return jsonify({"error": "price required"}), 400

    car["price"] = float(data["price"])
    return jsonify({"status": "success", "data": car}), 200


@app.route("/api/v1/car/<int:car_id>/status", methods=["PATCH"])
@jwt_required()
def mark_sold(car_id):
    """Owner marks ad as sold."""
    uid = get_jwt_identity()
    car = find_car(car_id)
    if not car:
        return jsonify({"error": "Car not found"}), 404
    if car["owner"] != uid:
        return jsonify({"error": "Forbidden"}), 403

    data = request.get_json() or {}
    new_status = data.get("status")
    if new_status not in {"sold", "available"}:
        return jsonify({"error": "status must be 'sold' or 'available'"}), 400

    car["status"] = new_status
    return jsonify({"status": "success", "data": car}), 200


@app.route("/api/v1/car", methods=["GET"])
def list_cars():
    """
    Public list with filters:
      - status (available/sold)
      - manufacturer
      - body_type
      - min_price / max_price
      - state (new/used)
    """
    status = request.args.get("status")
    manufacturer = request.args.get("manufacturer")
    body_type = request.args.get("body_type")
    state = request.args.get("state")
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)

    result = cars[:]
    if status:
        result = [c for c in result if c["status"] == status]
    if manufacturer:
        result = [c for c in result if c["manufacturer"].lower() == manufacturer.lower()]
    if body_type:
        result = [c for c in result if c["body_type"].lower() == body_type.lower()]
    if state:
        result = [c for c in result if c["state"] == state]
    if min_price is not None:
        result = [c for c in result if c["price"] >= min_price]
    if max_price is not None:
        result = [c for c in result if c["price"] <= max_price]

    return jsonify({"status": "success", "data": result}), 200


@app.route("/api/v1/car/<int:car_id>", methods=["GET"])
def get_car(car_id):
    car = find_car(car_id)
    if not car:
        return jsonify({"error": "Car not found"}), 404
    return jsonify({"status": "success", "data": car}), 200


if __name__ == "__main__":
    app.run(debug=True)

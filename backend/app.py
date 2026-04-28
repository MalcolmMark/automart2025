import os
from datetime import datetime, timedelta, timezone

from flask import Flask, Blueprint, jsonify, request
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)
from werkzeug.security import check_password_hash, generate_password_hash

# Temporary in-memory stores (replace with DB in production)
users = []
cars = []
orders = []

# Fast lookup indexes for the in-memory data.
users_by_id = {}
users_by_email = {}
cars_by_id = {}
orders_by_id = {}


auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")
car_bp = Blueprint("car", __name__, url_prefix="/api/v1/car")
admin_bp = Blueprint("admin", __name__, url_prefix="/api/v1/admin")
order_bp = Blueprint("order", __name__, url_prefix="/api/v1/order")


def _get_jwt_secret() -> str:
    try:
        return os.environ["JWT_SECRET_KEY"]
    except KeyError as exc:
        raise RuntimeError(
            "JWT_SECRET_KEY environment variable must be set (no hard-coded secrets)."
        ) from exc


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _find_user(user_id: int):
    return users_by_id.get(user_id)


def _auth_user():
    identity = get_jwt_identity()
    claims = get_jwt()
    try:
        user_id = int(identity)
    except (TypeError, ValueError):
        user_id = 0
    user = _find_user(user_id)
    return user, claims


def _find_car(car_id: int):
    return cars_by_id.get(car_id)


def _serialize_car(car):
    return {
        "id": car["id"],
        "owner": car["owner"],
        "created_on": car["created_on"],
        "state": car["state"],
        "status": car["status"],
        "price": car["price"],
        "manufacturer": car["manufacturer"],
        "model": car["model"],
        "body_type": car["body_type"],
    }


def _serialize_order(order):
    return {
        "id": order["id"],
        "buyer": order["buyer"],
        "car_id": order["car_id"],
        "created_on": order["created_on"],
        "status": order["status"],
        "price": order["price"],
        "price_offered": order["price_offered"],
        "old_price_offered": order.get("old_price_offered"),
    }


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True) or {}

    required_fields = ["email", "first_name", "last_name", "password", "address"]
    missing = [field for field in required_fields if not data.get(field)]
    if missing:
        return jsonify({"error": "Missing required fields", "missing_fields": missing}), 400

    email = data["email"].strip().lower()
    if email in users_by_email:
        return jsonify({"error": "User already exists"}), 400

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
        "password_hash": generate_password_hash(data["password"], method="pbkdf2:sha256"),
    }
    users.append(user)
    users_by_id[user_id] = user
    users_by_email[email] = user

    access_token = create_access_token(identity=str(user["id"]), additional_claims={"is_admin": user["is_admin"]})
    return (
        jsonify(
            {
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
        ),
        201,
    )


@auth_bp.route("/signin", methods=["POST"])
def signin():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = users_by_email.get(email)
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid email or password"}), 400

    access_token = create_access_token(identity=str(user["id"]), additional_claims={"is_admin": user["is_admin"]})
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


@car_bp.route("", methods=["POST"])
@jwt_required()
def create_car():
    user, _ = _auth_user()
    if not user:
        return jsonify({"error": "User not found"}), 401

    data = request.get_json(silent=True) or {}
    required_fields = ["state", "price", "manufacturer", "model", "body_type"]
    missing = [field for field in required_fields if data.get(field) in (None, "")]
    if missing:
        return jsonify({"error": "Missing required fields", "missing_fields": missing}), 400

    try:
        price = float(data["price"])
        if price <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"error": "price must be a positive number"}), 400

    car_id = len(cars) + 1
    car = {
        "id": car_id,
        "owner": user["id"],
        "created_on": _now_iso(),
        "state": str(data["state"]).strip().lower(),
        "status": "available",
        "price": round(price, 2),
        "manufacturer": str(data["manufacturer"]).strip(),
        "model": str(data["model"]).strip(),
        "body_type": str(data["body_type"]).strip(),
    }
    cars.append(car)
    cars_by_id[car_id] = car
    return jsonify({"message": "Car ad posted", "car": _serialize_car(car)}), 201


@car_bp.route("/<int:car_id>", methods=["GET"])
def get_car(car_id: int):
    car = _find_car(car_id)
    if not car:
        return jsonify({"error": "Car not found"}), 404
    return jsonify({"car": _serialize_car(car)}), 200


@car_bp.route("", methods=["GET"])
def get_unsold_cars():
    page = request.args.get("page", default=1, type=int)
    limit = request.args.get("limit", default=20, type=int)
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    manufacturer = request.args.get("manufacturer", default="", type=str).strip().lower()
    state = request.args.get("state", default="", type=str).strip().lower()
    body_type = request.args.get("body_type", default="", type=str).strip().lower()
    sort = request.args.get("sort", default="newest", type=str).strip().lower()

    if page < 1 or limit < 1 or limit > 100:
        return jsonify({"error": "page must be >= 1 and limit must be between 1 and 100"}), 400

    filtered = [car for car in cars if car["status"] == "available"]
    if min_price is not None:
        filtered = [car for car in filtered if car["price"] >= min_price]
    if max_price is not None:
        filtered = [car for car in filtered if car["price"] <= max_price]
    if manufacturer:
        filtered = [car for car in filtered if car["manufacturer"].strip().lower() == manufacturer]
    if state:
        filtered = [car for car in filtered if car["state"] == state]
    if body_type:
        filtered = [car for car in filtered if car["body_type"].strip().lower() == body_type]

    if sort == "price_asc":
        filtered = sorted(filtered, key=lambda car: car["price"])
    elif sort == "price_desc":
        filtered = sorted(filtered, key=lambda car: car["price"], reverse=True)
    else:
        filtered = sorted(filtered, key=lambda car: car["id"], reverse=True)

    total = len(filtered)
    start = (page - 1) * limit
    paged = filtered[start : start + limit]

    return (
        jsonify(
            {
                "cars": [_serialize_car(car) for car in paged],
                "count": len(paged),
                "total": total,
                "page": page,
                "limit": limit,
            }
        ),
        200,
    )


@car_bp.route("/<int:car_id>/status", methods=["PATCH"])
@jwt_required()
def mark_car_sold(car_id: int):
    user, _ = _auth_user()
    if not user:
        return jsonify({"error": "User not found"}), 401

    car = _find_car(car_id)
    if not car:
        return jsonify({"error": "Car not found"}), 404
    if car["owner"] != user["id"]:
        return jsonify({"error": "Only the seller can update this ad"}), 403

    car["status"] = "sold"
    return jsonify({"message": "Car marked as sold", "car": _serialize_car(car)}), 200


@car_bp.route("/<int:car_id>/price", methods=["PATCH"])
@jwt_required()
def update_car_price(car_id: int):
    user, _ = _auth_user()
    if not user:
        return jsonify({"error": "User not found"}), 401

    car = _find_car(car_id)
    if not car:
        return jsonify({"error": "Car not found"}), 404
    if car["owner"] != user["id"]:
        return jsonify({"error": "Only the seller can update this ad"}), 403

    data = request.get_json(silent=True) or {}
    try:
        price = float(data.get("price"))
        if price <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"error": "price must be a positive number"}), 400

    car["price"] = round(price, 2)
    return jsonify({"message": "Car price updated", "car": _serialize_car(car)}), 200


@order_bp.route("", methods=["POST"])
@jwt_required()
def create_order():
    user, _ = _auth_user()
    if not user:
        return jsonify({"error": "User not found"}), 401

    data = request.get_json(silent=True) or {}
    car_id = data.get("car_id")
    if not car_id:
        return jsonify({"error": "car_id is required"}), 400

    car = _find_car(int(car_id))
    if not car:
        return jsonify({"error": "Car not found"}), 404
    if car["status"] != "available":
        return jsonify({"error": "Cannot place order for a sold car"}), 400
    if car["owner"] == user["id"]:
        return jsonify({"error": "Cannot place an order on your own car"}), 400

    try:
        offered = float(data.get("amount"))
        if offered <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"error": "amount must be a positive number"}), 400

    order_id = len(orders) + 1
    order = {
        "id": order_id,
        "buyer": user["id"],
        "car_id": car["id"],
        "created_on": _now_iso(),
        "status": "pending",
        "price": car["price"],
        "price_offered": round(offered, 2),
    }
    orders.append(order)
    orders_by_id[order_id] = order
    return jsonify({"message": "Order created", "order": _serialize_order(order)}), 201


@order_bp.route("/<int:order_id>/price", methods=["PATCH"])
@jwt_required()
def update_order_price(order_id: int):
    user, _ = _auth_user()
    if not user:
        return jsonify({"error": "User not found"}), 401

    order = orders_by_id.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    if order["buyer"] != user["id"]:
        return jsonify({"error": "Only the buyer can update this order"}), 403

    data = request.get_json(silent=True) or {}
    try:
        offered = float(data.get("amount"))
        if offered <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"error": "amount must be a positive number"}), 400

    order["old_price_offered"] = order["price_offered"]
    order["price_offered"] = round(offered, 2)
    return jsonify({"message": "Order price updated", "order": _serialize_order(order)}), 200


@admin_bp.route("/car", methods=["GET"])
@jwt_required()
def list_all_cars_admin():
    user, _ = _auth_user()
    if not user:
        return jsonify({"error": "User not found"}), 401
    if not user["is_admin"]:
        return jsonify({"error": "Admin access required"}), 403

    return jsonify({"cars": [_serialize_car(car) for car in cars], "count": len(cars)}), 200


@car_bp.route("/<int:car_id>", methods=["DELETE"])
@jwt_required()
def delete_car(car_id: int):
    user, _ = _auth_user()
    if not user:
        return jsonify({"error": "User not found"}), 401
    if not user["is_admin"]:
        return jsonify({"error": "Admin access required"}), 403

    car = _find_car(car_id)
    if not car:
        return jsonify({"error": "Car not found"}), 404

    cars.remove(car)
    cars_by_id.pop(car_id, None)
    return jsonify({"message": "Car ad deleted"}), 200


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = _get_jwt_secret()
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)
    app.config.setdefault("TESTING", False)

    JWTManager(app)

    @app.route("/")
    def home():
        return jsonify({"message": "AutoMart API v1 running"}), 200

    app.register_blueprint(auth_bp)
    app.register_blueprint(car_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(admin_bp)

    return app


if __name__ == "__main__":
    application = create_app()
    isinstance(application, Flask)

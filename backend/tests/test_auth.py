import os
import pathlib
import sys

import pytest

os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret-key-with-minimum-32-bytes")
os.environ.setdefault("ADMIN_SIGNUP_CODE", "test-admin-code")

BASE_DIR = pathlib.Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app import cars, create_app, orders, users  # noqa: E402


@pytest.fixture
def client():
    users.clear()
    cars.clear()
    orders.clear()

    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def signup_and_token(client, email, *, admin=False):
    payload = {
        "email": email,
        "first_name": "Test",
        "last_name": "User",
        "password": "supersecret",
        "address": "Kampala",
    }
    if admin:
        payload["admin_code"] = "test-admin-code"

    res = client.post("/api/v1/auth/signup", json=payload)
    assert res.status_code == 201
    return res.get_json()["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_api_running(client):
    res = client.get("/")
    assert res.status_code == 200
    assert res.get_json()["message"] == "AutoMart API v1 running"


def test_signup_and_signin(client):
    payload = {
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "123456",
        "address": "Kampala",
    }
    res_signup = client.post("/api/v1/auth/signup", json=payload)
    assert res_signup.status_code == 201
    assert "access_token" in res_signup.get_json()

    res_signin = client.post(
        "/api/v1/auth/signin", json={"email": "test@example.com", "password": "123456"}
    )
    assert res_signin.status_code == 200
    assert res_signin.get_json()["user"]["is_admin"] is False


def test_signup_duplicate_email(client):
    payload = {
        "email": "duplicate@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "123456",
        "address": "Kampala",
    }
    assert client.post("/api/v1/auth/signup", json=payload).status_code == 201
    res = client.post("/api/v1/auth/signup", json=payload)
    assert res.status_code == 400
    assert "User already exists" in res.get_json()["error"]


def test_seller_car_lifecycle_and_filter(client):
    seller_token = signup_and_token(client, "seller@example.com")

    post_res = client.post(
        "/api/v1/car",
        json={
            "state": "new",
            "price": 15000,
            "manufacturer": "Toyota",
            "model": "Corolla",
            "body_type": "Sedan",
        },
        headers=auth_headers(seller_token),
    )
    assert post_res.status_code == 201
    car_id = post_res.get_json()["car"]["id"]

    get_res = client.get(f"/api/v1/car/{car_id}")
    assert get_res.status_code == 200
    assert get_res.get_json()["car"]["status"] == "available"

    update_res = client.patch(
        f"/api/v1/car/{car_id}/price",
        json={"price": 14500},
        headers=auth_headers(seller_token),
    )
    assert update_res.status_code == 200
    assert update_res.get_json()["car"]["price"] == 14500.0

    filter_res = client.get("/api/v1/car?min_price=14000&max_price=14600")
    assert filter_res.status_code == 200
    assert filter_res.get_json()["count"] == 1

    sold_res = client.patch(
        f"/api/v1/car/{car_id}/status",
        headers=auth_headers(seller_token),
    )
    assert sold_res.status_code == 200
    assert sold_res.get_json()["car"]["status"] == "sold"

    available_res = client.get("/api/v1/car")
    assert available_res.status_code == 200
    assert available_res.get_json()["count"] == 0


def test_buyer_order_and_update_offer(client):
    seller_token = signup_and_token(client, "seller2@example.com")
    buyer_token = signup_and_token(client, "buyer@example.com")

    car_res = client.post(
        "/api/v1/car",
        json={
            "state": "used",
            "price": 8000,
            "manufacturer": "Honda",
            "model": "Civic",
            "body_type": "Hatchback",
        },
        headers=auth_headers(seller_token),
    )
    car_id = car_res.get_json()["car"]["id"]

    order_res = client.post(
        "/api/v1/order",
        json={"car_id": car_id, "amount": 7600},
        headers=auth_headers(buyer_token),
    )
    assert order_res.status_code == 201
    order_data = order_res.get_json()["order"]
    assert order_data["price"] == 8000.0
    assert order_data["price_offered"] == 7600.0

    update_order_res = client.patch(
        f"/api/v1/order/{order_data['id']}/price",
        json={"amount": 7800},
        headers=auth_headers(buyer_token),
    )
    assert update_order_res.status_code == 200
    updated = update_order_res.get_json()["order"]
    assert updated["old_price_offered"] == 7600.0
    assert updated["price_offered"] == 7800.0


def test_admin_can_view_and_delete_ads(client):
    seller_token = signup_and_token(client, "seller3@example.com")
    admin_token = signup_and_token(client, "admin@example.com", admin=True)

    car_res = client.post(
        "/api/v1/car",
        json={
            "state": "used",
            "price": 9900,
            "manufacturer": "Subaru",
            "model": "Impreza",
            "body_type": "Sedan",
        },
        headers=auth_headers(seller_token),
    )
    car_id = car_res.get_json()["car"]["id"]

    list_res = client.get("/api/v1/admin/car", headers=auth_headers(admin_token))
    assert list_res.status_code == 200
    assert list_res.get_json()["count"] == 1

    delete_res = client.delete(f"/api/v1/car/{car_id}", headers=auth_headers(admin_token))
    assert delete_res.status_code == 200

    list_after = client.get("/api/v1/admin/car", headers=auth_headers(admin_token))
    assert list_after.get_json()["count"] == 0


def test_non_admin_cannot_delete_car(client):
    seller_token = signup_and_token(client, "seller4@example.com")
    buyer_token = signup_and_token(client, "buyer2@example.com")

    car_res = client.post(
        "/api/v1/car",
        json={
            "state": "used",
            "price": 6500,
            "manufacturer": "Nissan",
            "model": "Note",
            "body_type": "Hatchback",
        },
        headers=auth_headers(seller_token),
    )
    car_id = car_res.get_json()["car"]["id"]

    forbidden = client.delete(f"/api/v1/car/{car_id}", headers=auth_headers(buyer_token))
    assert forbidden.status_code == 403
    assert forbidden.get_json()["error"] == "Admin access required"

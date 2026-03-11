import os
import sys
import pathlib

import pytest

# Ensure env vars exist for tests
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret")
os.environ.setdefault("ADMIN_SIGNUP_CODE", "test-admin-code")

# Ensure the backend root (where app.py lives) is on sys.path
BASE_DIR = pathlib.Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app import create_app, users  # noqa: E402  (import after path setup)


@pytest.fixture
def client():
    """
    Fresh test client + clean in-memory store per test.
    """
    users.clear()
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_api_running(client):
    res = client.get("/")
    assert res.status_code == 200
    data = res.get_json()
    assert data["message"] == "AutoMart API v1 running"


def test_signup_success(client):
    payload = {
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "123456",
        "address": "Kampala",
        # no admin_code → normal user
    }
    res = client.post("/api/v1/auth/signup", json=payload)
    assert res.status_code == 201
    data = res.get_json()
    assert data["user"]["email"] == "test@example.com"
    assert data["user"]["is_admin"] is False
    assert "access_token" in data


def test_signup_duplicate_email(client):
    payload = {
        "email": "duplicate@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "123456",
        "address": "Kampala",
    }
    # First signup
    res1 = client.post("/api/v1/auth/signup", json=payload)
    assert res1.status_code == 201

    # Second signup with same email should fail
    res2 = client.post("/api/v1/auth/signup", json=payload)
    assert res2.status_code == 400
    data = res2.get_json()
    assert "User already exists" in data["error"]


def test_signin_success_as_admin(client):
    # sign up first with valid admin_code
    signup_payload = {
        "email": "login@example.com",
        "first_name": "Login",
        "last_name": "User",
        "password": "supersecret",
        "address": "Kampala",
        "admin_code": "test-admin-code",  # matches ADMIN_SIGNUP_CODE
    }
    res_signup = client.post("/api/v1/auth/signup", json=signup_payload)
    assert res_signup.status_code == 201
    signup_data = res_signup.get_json()
    assert signup_data["user"]["is_admin"] is True

    # then login with same credentials
    signin_payload = {
        "email": "login@example.com",
        "password": "supersecret",
    }
    res_signin = client.post("/api/v1/auth/signin", json=signin_payload)
    assert res_signin.status_code == 200
    data = res_signin.get_json()
    assert "access_token" in data
    assert data["user"]["is_admin"] is True


def test_signin_invalid_credentials(client):
    # no user created
    payload = {"email": "nosuchuser@example.com", "password": "wrong"}
    res = client.post("/api/v1/auth/signin", json=payload)
    assert res.status_code == 400
    data = res.get_json()
    assert "Invalid email or password" in data["error"]
    assert "access_token" not in data
    payload = {"email": "sales@eclipsebiosciences.com", "password": "incorect"}
    payload = {"email": "", "password": "incorect"} 
#current point i stopped
#Codedex.dex
#     res = client.post("/api/v1/auth/signin", json=payload)
#     assert res.status_code == 400
#     data = res.get_json()
#     assert "Invalid email or password" in data["error"]   
#     payload = {"email": "malcolmamamrokabo@gmail.com", "password": ""}
#     res = client.post("/api/v1/auth/signin", json=payload)
#     assert res.status_code == 400
#     data = res.get_json()             
#     assert "Invalid email or password" in data["error"]   
#     payload = {"email": "malcolmamamrokabo@gmail.com", "password": ""}
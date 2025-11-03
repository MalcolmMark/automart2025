from app import app

def test_api_running():
    client = app.test_client()
    res = client.get("/")
    assert res.status_code == 200

def test_signup():
    client = app.test_client()
    res = client.post("/api/v1/auth/signup", json={
        "email": "test@example.com",
        "password": "123456"
    })
    assert res.status_code == 201

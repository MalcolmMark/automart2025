from backend.app import app
import json

def _signin_token(client, email="owner@example.com", password="123456"):
    # ensure user exists
    client.post("/api/v1/auth/signup", json={"email": email, "password": password})
    res = client.post("/api/v1/auth/signin", json={"email": email, "password": password})
    assert res.status_code == 200
    return res.get_json()["data"]["token"]

def test_create_update_list_get_car():
    client = app.test_client()

    # auth
    token = _signin_token(client)

    # create car
    new_car = {
        "manufacturer": "Toyota",
        "model": "Corolla",
        "price": 5000,
        "state": "used",
        "body_type": "sedan",
        "description": "nice car"
    }
    res = client.post(
        "/api/v1/car",
        json=new_car,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 201
    car = res.get_json()["data"]
    car_id = car["id"]

    # update price
    res = client.patch(
        f"/api/v1/car/{car_id}/price",
        json={"price": 5200},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    assert res.get_json()["data"]["price"] == 5200.0

    # mark sold
    res = client.patch(
        f"/api/v1/car/{car_id}/status",
        json={"status": "sold"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    assert res.get_json()["data"]["status"] == "sold"

    # list with filters (e.g., status=sold)
    res = client.get("/api/v1/car?status=sold")
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert any(c["id"] == car_id for c in data)

    # get single
    res = client.get(f"/api/v1/car/{car_id}")
    assert res.status_code == 200
    assert res.get_json()["data"]["id"] == car_id

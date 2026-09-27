import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_signup_and_login_flow():
    test_phone = "+919999999099"
    test_password = "SecurePassword123!"
    
    # 1. Test signup
    signup_res = client.post("/api/signup", json={
        "phone_number": test_phone,
        "password": test_password,
        "language": "hi",
        "location": "Madhya Pradesh, India"
    })
    # If already registered from previous run, accept 200 or 400
    assert signup_res.status_code in (200, 400)
    
    # 2. Test login
    login_res = client.post("/api/login", json={
        "phone_number": test_phone,
        "password": test_password
    })
    assert login_res.status_code == 200
    data = login_res.json()
    assert "access_token" in data
    token = data["access_token"]
    
    # 3. Test /api/me with Bearer token
    me_res = client.get("/api/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["phone_number"] == test_phone
    assert me_data["language"] == "hi"

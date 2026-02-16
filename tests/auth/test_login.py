import pytest

@pytest.fixture
def registered_user(client, fake):
    email = fake.unique.email()
    password = fake.password(length=12)
    res = client.post("/auth/register", json={"email": email, "password": password})
    assert res.status_code == 201
    return {"email": email, "password": password}


def test_login_success(client, registered_user):
    res = client.post("/auth/login", json=registered_user)

    assert res.status_code == 200
    body = res.get_json()
    assert body["email"] == registered_user["email"]
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["expires_in"] == 900


def test_login_wrong_password(client, registered_user):
    res = client.post("/auth/login", json={"email": registered_user["email"], "password": "wrong"})
    assert res.status_code == 401
    assert res.get_json()["error"] == "Invalid email or password"


def test_login_missing_fields(client):
    res = client.post("/auth/login", json={"email": "", "password": ""})
    assert res.status_code == 400
    assert res.get_json()["error"] == "email and password required"
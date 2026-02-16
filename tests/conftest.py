import os
import pytest
from faker import Faker

from backend.app.main import app


@pytest.fixture
def client():
    client = app.test_client()
    client.preserve_context = False
    return client


@pytest.fixture()
def auth_headers():
    def _make(access_token: str) -> dict:
        return {"Authorization": f"Bearer {access_token}"}
    return _make

@pytest.fixture
def fake():
    return Faker()

@pytest.fixture
def authenticated_user(client, fake):
    email = fake.email()
    password = fake.password(length=12)

    client.post("/auth/register", json={"email": email, "password": password})
    res = client.post("/auth/login", json={"email": email, "password": password})

    body = res.get_json()

    return {
        "email": email,
        "password": password,
        "access_token": body["access_token"],
        "refresh_token": body["refresh_token"],
    }
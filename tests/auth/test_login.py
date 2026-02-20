import pytest
from assertpy import assert_that


@pytest.fixture
def registered_user(client, fake):
    email = fake.unique.email()
    password = fake.password(length=12)
    res = client.post("/auth/register", json={"email": email, "password": password})
    assert_that(res.status_code).described_as("register before login").is_equal_to(201)
    return {"email": email, "password": password}


def test_login_success(client, registered_user):
    res = client.post("/auth/login", json=registered_user)

    assert_that(res.status_code).described_as("status").is_equal_to(200)
    body = res.get_json()
    assert_that(body["email"]).described_as("email").is_equal_to(registered_user["email"])
    assert_that(body).described_as("token fields").contains_key("access_token", "refresh_token")
    assert_that(body["expires_in"]).described_as("expires_in").is_equal_to(900)


def test_login_wrong_password(client, registered_user):
    res = client.post(
        "/auth/login", json={"email": registered_user["email"], "password": "wrong"}
    )
    assert_that(res.status_code).described_as("status").is_equal_to(401)
    assert_that(res.get_json()["error"]).described_as("error message").is_equal_to("Invalid email or password")


def test_login_missing_fields(client):
    res = client.post("/auth/login", json={"email": "", "password": ""})
    assert_that(res.status_code).described_as("status").is_equal_to(400)
    assert_that(res.get_json()["error"]).described_as("error message").is_equal_to("email and password required")

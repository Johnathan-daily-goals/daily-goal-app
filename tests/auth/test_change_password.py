import pytest
from assertpy import assert_that


@pytest.fixture
def registered_user(client, fake):
    email = fake.unique.email()
    password = fake.password(length=12)
    res = client.post("/auth/register", json={"email": email, "password": password})
    assert_that(res.status_code).described_as("register status").is_equal_to(201)
    body = res.get_json()
    return {"email": email, "password": password, "access_token": body["access_token"]}


def test_change_password_success(client, registered_user, fake):
    new_password = fake.password(length=12)
    res = client.post(
        "/auth/change-password",
        headers={"Authorization": f"Bearer {registered_user['access_token']}"},
        json={"current_password": registered_user["password"], "new_password": new_password},
    )
    assert_that(res.status_code).described_as("status").is_equal_to(200)
    assert_that(res.get_json()["status"]).described_as("status field").is_equal_to("password_changed")


def test_change_password_can_login_with_new_password(client, registered_user, fake):
    new_password = fake.password(length=12)
    client.post(
        "/auth/change-password",
        headers={"Authorization": f"Bearer {registered_user['access_token']}"},
        json={"current_password": registered_user["password"], "new_password": new_password},
    )
    res = client.post("/auth/login", json={"email": registered_user["email"], "password": new_password})
    assert_that(res.status_code).described_as("login with new password status").is_equal_to(200)


def test_change_password_old_password_no_longer_works(client, registered_user, fake):
    new_password = fake.password(length=12)
    client.post(
        "/auth/change-password",
        headers={"Authorization": f"Bearer {registered_user['access_token']}"},
        json={"current_password": registered_user["password"], "new_password": new_password},
    )
    res = client.post("/auth/login", json={"email": registered_user["email"], "password": registered_user["password"]})
    assert_that(res.status_code).described_as("login with old password status").is_equal_to(401)


def test_change_password_wrong_current_password(client, registered_user, fake):
    res = client.post(
        "/auth/change-password",
        headers={"Authorization": f"Bearer {registered_user['access_token']}"},
        json={"current_password": "wrongpassword", "new_password": fake.password(length=12)},
    )
    assert_that(res.status_code).described_as("status").is_equal_to(401)
    assert_that(res.get_json()["error"]).described_as("error message").is_equal_to("Current password is incorrect")


def test_change_password_missing_fields(client, registered_user):
    res = client.post(
        "/auth/change-password",
        headers={"Authorization": f"Bearer {registered_user['access_token']}"},
        json={},
    )
    assert_that(res.status_code).described_as("status").is_equal_to(400)


def test_change_password_requires_auth(client, fake):
    res = client.post(
        "/auth/change-password",
        json={"current_password": "x", "new_password": "y"},
    )
    assert_that(res.status_code).described_as("status").is_equal_to(401)

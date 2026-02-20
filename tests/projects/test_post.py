import pytest
from assertpy import assert_that


@pytest.fixture
def auth_headers(authenticated_user):
    return {"Authorization": f"Bearer {authenticated_user['access_token']}"}


def test_create_project_success(client, auth_headers, fake):
    res = client.post(
        "/projects",
        headers=auth_headers,
        json={"name": fake.word(), "description": fake.sentence()},
    )
    assert_that(res.status_code).described_as("status").is_equal_to(201)
    body = res.get_json()
    assert_that(body).described_as("response fields").contains_key("id", "name")


def test_create_project_missing_name(client, auth_headers):
    res = client.post("/projects", headers=auth_headers, json={"description": "x"})
    assert_that(res.status_code).described_as("status").is_equal_to(400)
    assert_that(res.get_json()["error"]).described_as("error message").is_equal_to("Project name required")


def test_create_project_requires_auth(client):
    res = client.post("/projects", json={"name": "x"})
    assert_that(res.status_code).described_as("status").is_equal_to(401)

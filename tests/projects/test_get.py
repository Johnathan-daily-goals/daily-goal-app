import pytest
from assertpy import assert_that


@pytest.fixture
def auth_headers(authenticated_user):
    return {"Authorization": f"Bearer {authenticated_user['access_token']}"}


@pytest.fixture
def created_project(client, auth_headers):
    res = client.post(
        "/projects", headers=auth_headers, json={"name": "Test", "description": "Desc"}
    )
    assert_that(res.status_code).described_as("create project status").is_equal_to(201)
    return res.get_json()


def test_get_projects_returns_list(client, auth_headers):
    res = client.get("/projects", headers=auth_headers)
    assert_that(res.status_code).described_as("status").is_equal_to(200)
    assert_that(res.get_json()).described_as("response body").is_instance_of(list)


def test_get_projects_includes_created_project(client, auth_headers, created_project):
    res = client.get("/projects", headers=auth_headers)
    assert_that(res.status_code).described_as("status").is_equal_to(200)
    ids = [p["id"] for p in res.get_json()]
    assert_that(ids).described_as("project ids").contains(created_project["id"])


def test_get_projects_requires_auth(client):
    res = client.get("/projects")
    assert_that(res.status_code).described_as("status").is_equal_to(401)

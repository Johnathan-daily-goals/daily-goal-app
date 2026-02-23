import pytest
from assertpy import assert_that


@pytest.fixture
def auth_headers(authenticated_user):
    return {"Authorization": f"Bearer {authenticated_user['access_token']}"}


@pytest.fixture
def created_project(client, auth_headers):
    res = client.post(
        "/projects", headers=auth_headers, json={"name": "P", "description": "D"}
    )
    assert_that(res.status_code).described_as("create project status").is_equal_to(201)
    return res.get_json()


def test_get_project_success(client, auth_headers, created_project):
    project_id = created_project["id"]
    res = client.get(f"/projects/{project_id}", headers=auth_headers)
    assert_that(res.status_code).described_as("status").is_equal_to(200)
    assert_that(res.get_json()["id"]).described_as("project id").is_equal_to(project_id)


def test_get_project_not_found(client, auth_headers):
    res = client.get("/projects/999999", headers=auth_headers)
    assert_that(res.status_code).described_as("status").is_equal_to(404)
    assert_that(res.get_json()["error"]).described_as("error message").is_equal_to("Project not found")


def test_get_project_requires_auth(client, created_project):
    res = client.get(f"/projects/{created_project['id']}")
    assert_that(res.status_code).described_as("status").is_equal_to(401)

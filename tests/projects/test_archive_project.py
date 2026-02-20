import pytest
from assertpy import assert_that


@pytest.fixture
def auth_headers(authenticated_user):
    return {"Authorization": f"Bearer {authenticated_user['access_token']}"}


@pytest.fixture
def created_project(client, auth_headers):
    res = client.post(
        "/projects", headers=auth_headers, json={"name": "A", "description": ""}
    )
    assert_that(res.status_code).described_as("create project status").is_equal_to(201)
    return res.get_json()


def test_archive_project_success(client, auth_headers, created_project):
    project_id = created_project["id"]
    res = client.post(f"/projects/{project_id}/archive", headers=auth_headers)
    assert_that(res.status_code).described_as("status").is_equal_to(200)
    assert_that(res.get_json()["status"]).described_as("archive status").is_equal_to("archived")


def test_archive_project_already_archived_conflict(client, auth_headers, created_project):
    project_id = created_project["id"]
    first = client.post(f"/projects/{project_id}/archive", headers=auth_headers)
    assert_that(first.status_code).described_as("first archive status").is_equal_to(200)

    second = client.post(f"/projects/{project_id}/archive", headers=auth_headers)
    assert_that(second.status_code).described_as("duplicate archive status").is_equal_to(409)
    assert_that(second.get_json()["error"]).described_as("error message").is_equal_to("Project already archived")


def test_archive_project_not_found(client, auth_headers):
    res = client.post("/projects/999999/archive", headers=auth_headers)
    assert_that(res.status_code).described_as("status").is_equal_to(404)

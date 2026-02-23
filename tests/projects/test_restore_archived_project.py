import pytest
from assertpy import assert_that


@pytest.fixture
def auth_headers(authenticated_user):
    return {"Authorization": f"Bearer {authenticated_user['access_token']}"}


@pytest.fixture
def archived_project(client, auth_headers):
    created = client.post(
        "/projects", headers=auth_headers, json={"name": "R", "description": ""}
    )
    assert_that(created.status_code).described_as("create project status").is_equal_to(201)
    project_id = created.get_json()["id"]

    archived = client.post(f"/projects/{project_id}/archive", headers=auth_headers)
    assert_that(archived.status_code).described_as("archive status").is_equal_to(200)

    return project_id


def test_restore_project_success(client, auth_headers, archived_project):
    res = client.post(f"/projects/{archived_project}/restore", headers=auth_headers)
    assert_that(res.status_code).described_as("status").is_equal_to(200)
    assert_that(res.get_json()["status"]).described_as("restore status").is_equal_to("restored")


def test_restore_project_not_archived_conflict(client, auth_headers):
    created = client.post(
        "/projects", headers=auth_headers, json={"name": "N", "description": ""}
    )
    project_id = created.get_json()["id"]

    res = client.post(f"/projects/{project_id}/restore", headers=auth_headers)
    assert_that(res.status_code).described_as("status").is_equal_to(409)
    assert_that(res.get_json()["error"]).described_as("error message").is_equal_to("Project is not archived")


def test_restore_project_not_found(client, auth_headers):
    res = client.post("/projects/999999/restore", headers=auth_headers)
    assert_that(res.status_code).described_as("status").is_equal_to(404)

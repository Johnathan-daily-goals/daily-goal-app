import pytest
from assertpy import assert_that


@pytest.fixture
def auth_headers(authenticated_user):
    return {"Authorization": f"Bearer {authenticated_user['access_token']}"}


@pytest.fixture
def archived_project(client, auth_headers):
    created = client.post(
        "/projects", headers=auth_headers, json={"name": "X", "description": ""}
    )
    assert_that(created.status_code).described_as("create project status").is_equal_to(201)
    project_id = created.get_json()["id"]

    archived = client.post(f"/projects/{project_id}/archive", headers=auth_headers)
    assert_that(archived.status_code).described_as("archive status").is_equal_to(200)

    return project_id


def test_get_archived_projects_returns_list(client, auth_headers):
    res = client.get("/projects/archived", headers=auth_headers)
    assert_that(res.status_code).described_as("status").is_equal_to(200)
    assert_that(res.get_json()).described_as("response body").is_instance_of(list)


def test_get_archived_projects_includes_archived_project(client, auth_headers, archived_project):
    res = client.get("/projects/archived", headers=auth_headers)
    ids = [p["id"] for p in res.get_json()]
    assert_that(ids).described_as("archived project ids").contains(archived_project)


def test_get_archived_projects_requires_auth(client):
    res = client.get("/projects/archived")
    assert_that(res.status_code).described_as("status").is_equal_to(401)

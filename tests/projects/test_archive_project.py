import pytest


@pytest.fixture
def auth_headers(authenticated_user):
    return {"Authorization": f"Bearer {authenticated_user['access_token']}"}


@pytest.fixture
def created_project(client, auth_headers):
    res = client.post(
        "/projects", headers=auth_headers, json={"name": "A", "description": ""}
    )
    assert res.status_code == 201
    return res.get_json()


def test_archive_project_success(client, auth_headers, created_project):
    project_id = created_project["id"]
    res = client.post(f"/projects/{project_id}/archive", headers=auth_headers)
    assert res.status_code == 200
    assert res.get_json()["status"] == "archived"


def test_archive_project_already_archived_conflict(
    client, auth_headers, created_project
):
    project_id = created_project["id"]
    first = client.post(f"/projects/{project_id}/archive", headers=auth_headers)
    assert first.status_code == 200

    second = client.post(f"/projects/{project_id}/archive", headers=auth_headers)
    assert second.status_code == 409
    assert second.get_json()["error"] == "Project already archived"


def test_archive_project_not_found(client, auth_headers):
    res = client.post("/projects/999999/archive", headers=auth_headers)
    assert res.status_code == 404

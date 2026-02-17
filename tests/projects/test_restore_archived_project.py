import pytest


@pytest.fixture
def auth_headers(authenticated_user):
    return {"Authorization": f"Bearer {authenticated_user['access_token']}"}


@pytest.fixture
def archived_project(client, auth_headers):
    created = client.post(
        "/projects", headers=auth_headers, json={"name": "R", "description": ""}
    )
    assert created.status_code == 201
    project_id = created.get_json()["id"]

    archived = client.post(f"/projects/{project_id}/archive", headers=auth_headers)
    assert archived.status_code == 200

    return project_id


def test_restore_project_success(client, auth_headers, archived_project):
    res = client.post(f"/projects/{archived_project}/restore", headers=auth_headers)
    assert res.status_code == 200
    assert res.get_json()["status"] == "restored"


def test_restore_project_not_archived_conflict(client, auth_headers):
    created = client.post(
        "/projects", headers=auth_headers, json={"name": "N", "description": ""}
    )
    project_id = created.get_json()["id"]

    res = client.post(f"/projects/{project_id}/restore", headers=auth_headers)
    assert res.status_code == 409
    assert res.get_json()["error"] == "Project is not archived"


def test_restore_project_not_found(client, auth_headers):
    res = client.post("/projects/999999/restore", headers=auth_headers)
    assert res.status_code == 404

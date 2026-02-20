import pytest


@pytest.fixture
def auth_headers(authenticated_user):
    return {"Authorization": f"Bearer {authenticated_user['access_token']}"}


@pytest.fixture
def created_project(client, auth_headers):
    res = client.post(
        "/projects", headers=auth_headers, json={"name": "Del", "description": ""}
    )
    assert res.status_code == 201
    return res.get_json()


def test_delete_project_archives_success(client, auth_headers, created_project):
    project_id = created_project["id"]
    res = client.delete(f"/projects/{project_id}", headers=auth_headers)
    assert res.status_code == 200
    assert res.get_json()["status"] == "archived"


def test_delete_project_not_found(client, auth_headers):
    res = client.delete("/projects/999999", headers=auth_headers)
    assert res.status_code == 404


def test_delete_project_requires_auth(client, created_project):
    res = client.delete(f"/projects/{created_project['id']}")
    assert res.status_code == 401

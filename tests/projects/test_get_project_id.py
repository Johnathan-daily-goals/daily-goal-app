import pytest

@pytest.fixture
def auth_headers(authenticated_user):
    return {"Authorization": f"Bearer {authenticated_user['access_token']}"}

@pytest.fixture
def created_project(client, auth_headers):
    res = client.post("/projects", headers=auth_headers, json={"name": "P", "description": "D"})
    assert res.status_code == 201
    return res.get_json()


def test_get_project_success(client, auth_headers, created_project):
    project_id = created_project["id"]
    res = client.get(f"/projects/{project_id}", headers=auth_headers)
    assert res.status_code == 200
    body = res.get_json()
    assert body["id"] == project_id


def test_get_project_not_found(client, auth_headers):
    res = client.get("/projects/999999", headers=auth_headers)
    assert res.status_code == 404
    assert res.get_json()["error"] == "Project not found"


def test_get_project_requires_auth(client, created_project):
    res = client.get(f"/projects/{created_project['id']}")
    assert res.status_code == 401
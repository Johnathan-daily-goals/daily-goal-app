import pytest

@pytest.fixture
def auth_headers(authenticated_user):
    return {"Authorization": f"Bearer {authenticated_user['access_token']}"}

@pytest.fixture
def archived_project(client, auth_headers):
    created = client.post("/projects", headers=auth_headers, json={"name": "X", "description": ""})
    assert created.status_code == 201
    project_id = created.get_json()["id"]

    archived = client.post(f"/projects/{project_id}/archive", headers=auth_headers)
    assert archived.status_code == 200

    return project_id


def test_get_archived_projects_returns_list(client, auth_headers):
    res = client.get("/projects/archived", headers=auth_headers)
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)


def test_get_archived_projects_includes_archived_project(client, auth_headers, archived_project):
    res = client.get("/projects/archived", headers=auth_headers)
    ids = [p["id"] for p in res.get_json()]
    assert archived_project in ids


def test_get_archived_projects_requires_auth(client):
    res = client.get("/projects/archived")
    assert res.status_code == 401
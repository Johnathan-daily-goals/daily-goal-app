import pytest


@pytest.fixture
def auth_headers(authenticated_user):
    return {"Authorization": f"Bearer {authenticated_user['access_token']}"}


@pytest.fixture
def created_project(client, auth_headers):
    res = client.post(
        "/projects", headers=auth_headers, json={"name": "Test", "description": "Desc"}
    )
    assert res.status_code == 201
    return res.get_json()


def test_get_projects_returns_list(client, auth_headers):
    res = client.get("/projects", headers=auth_headers)
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)


def test_get_projects_includes_created_project(client, auth_headers, created_project):
    res = client.get("/projects", headers=auth_headers)
    assert res.status_code == 200
    ids = [p["id"] for p in res.get_json()]
    assert created_project["id"] in ids


def test_get_projects_requires_auth(client):
    res = client.get("/projects")
    assert res.status_code == 401

import pytest

@pytest.fixture
def auth_headers(authenticated_user):
    return {"Authorization": f"Bearer {authenticated_user['access_token']}"}


def test_create_project_success(client, auth_headers, fake):
    res = client.post(
        "/projects",
        headers=auth_headers,
        json={"name": fake.word(), "description": fake.sentence()},
    )
    assert res.status_code == 201
    body = res.get_json()
    assert "id" in body
    assert "name" in body


def test_create_project_missing_name(client, auth_headers):
    res = client.post("/projects", headers=auth_headers, json={"description": "x"})
    assert res.status_code == 400
    assert res.get_json()["error"] == "Project name required"


def test_create_project_requires_auth(client):
    res = client.post("/projects", json={"name": "x"})
    assert res.status_code == 401
    
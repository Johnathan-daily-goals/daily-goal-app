import pytest


@pytest.fixture
def auth_headers(authenticated_user):
    return {"Authorization": f"Bearer {authenticated_user['access_token']}"}


@pytest.fixture
def created_project(client, auth_headers):
    res = client.post(
        "/projects", headers=auth_headers, json={"name": "G", "description": ""}
    )
    assert res.status_code == 201
    return res.get_json()["id"]


def test_create_daily_goal_success(client, auth_headers, created_project):
    res = client.post(
        f"/projects/{created_project}/goals",
        headers=auth_headers,
        json={"goal_text": "do the thing"},
    )
    assert res.status_code == 201
    body = res.get_json()
    assert "id" in body
    assert body["project_id"] == created_project


def test_create_daily_goal_missing_goal_text(client, auth_headers, created_project):
    res = client.post(
        f"/projects/{created_project}/goals", headers=auth_headers, json={}
    )
    assert res.status_code == 400
    assert res.get_json()["error"] == "goal_text required"


def test_create_daily_goal_project_not_found(client, auth_headers):
    res = client.post(
        "/projects/999999/goals", headers=auth_headers, json={"goal_text": "x"}
    )
    assert res.status_code == 404
    assert res.get_json()["error"] == "Project not found"

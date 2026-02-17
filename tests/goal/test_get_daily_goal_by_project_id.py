import pytest


@pytest.fixture
def auth_headers(authenticated_user):
    return {"Authorization": f"Bearer {authenticated_user['access_token']}"}


@pytest.fixture
def project_with_today_goal(client, auth_headers):
    created = client.post(
        "/projects", headers=auth_headers, json={"name": "TODAY", "description": ""}
    )
    project_id = created.get_json()["id"]

    upsert = client.put(
        f"/projects/{project_id}/goals/today",
        headers=auth_headers,
        json={"goal_text": "today goal"},
    )
    assert upsert.status_code in (200, 201)

    return project_id


def test_get_todays_goal_success(client, auth_headers, project_with_today_goal):
    res = client.get(
        f"/projects/{project_with_today_goal}/goals/today", headers=auth_headers
    )
    assert res.status_code == 200
    assert res.get_json()["goal_text"] == "today goal"


def test_get_todays_goal_not_set_returns_404(client, auth_headers):
    created = client.post(
        "/projects", headers=auth_headers, json={"name": "EMPTY", "description": ""}
    )
    project_id = created.get_json()["id"]

    res = client.get(f"/projects/{project_id}/goals/today", headers=auth_headers)
    assert res.status_code == 404
    assert res.get_json()["error"] == "No goal set for today"


def test_get_todays_goal_project_not_found(client, auth_headers):
    res = client.get("/projects/999999/goals/today", headers=auth_headers)
    assert res.status_code == 404
    assert res.get_json()["error"] == "Project not found"

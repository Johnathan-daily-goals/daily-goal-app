import pytest

@pytest.fixture
def auth_headers(authenticated_user):
    return {"Authorization": f"Bearer {authenticated_user['access_token']}"}

@pytest.fixture
def created_project(client, auth_headers):
    res = client.post("/projects", headers=auth_headers, json={"name": "UPSERT", "description": ""})
    assert res.status_code == 201
    return res.get_json()["id"]


def test_upsert_today_goal_creates(client, auth_headers, created_project):
    res = client.put(
        f"/projects/{created_project}/goals/today",
        headers=auth_headers,
        json={"goal_text": "first"},
    )
    assert res.status_code == 201
    assert res.get_json()["goal_text"] == "first"


def test_upsert_today_goal_updates(client, auth_headers, created_project):
    first = client.put(
        f"/projects/{created_project}/goals/today",
        headers=auth_headers,
        json={"goal_text": "first"},
    )
    assert first.status_code in (200, 201)

    second = client.put(
        f"/projects/{created_project}/goals/today",
        headers=auth_headers,
        json={"goal_text": "updated"},
    )
    assert second.status_code == 200
    assert second.get_json()["goal_text"] == "updated"


def test_upsert_today_goal_missing_goal_text(client, auth_headers, created_project):
    res = client.put(f"/projects/{created_project}/goals/today", headers=auth_headers, json={})
    assert res.status_code == 400
    assert res.get_json()["error"] == "goal_text required"
import pytest
from assertpy import assert_that


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
    assert_that(upsert.status_code).described_as("upsert today goal status").is_in(200, 201)

    return project_id


def test_get_todays_goal_success(client, auth_headers, project_with_today_goal):
    res = client.get(
        f"/projects/{project_with_today_goal}/goals/today", headers=auth_headers
    )
    assert_that(res.status_code).described_as("status").is_equal_to(200)
    assert_that(res.get_json()["goal_text"]).described_as("goal text").is_equal_to("today goal")


def test_get_todays_goal_not_set_returns_404(client, auth_headers):
    created = client.post(
        "/projects", headers=auth_headers, json={"name": "EMPTY", "description": ""}
    )
    project_id = created.get_json()["id"]

    res = client.get(f"/projects/{project_id}/goals/today", headers=auth_headers)
    assert_that(res.status_code).described_as("status").is_equal_to(404)
    assert_that(res.get_json()["error"]).described_as("error message").is_equal_to("No goal set for today")


def test_get_todays_goal_project_not_found(client, auth_headers):
    res = client.get("/projects/999999/goals/today", headers=auth_headers)
    assert_that(res.status_code).described_as("status").is_equal_to(404)
    assert_that(res.get_json()["error"]).described_as("error message").is_equal_to("Project not found")

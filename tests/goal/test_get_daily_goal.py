import pytest
from assertpy import assert_that


@pytest.fixture
def auth_headers(authenticated_user):
    return {"Authorization": f"Bearer {authenticated_user['access_token']}"}


@pytest.fixture
def project_with_goal(client, auth_headers):
    created = client.post(
        "/projects", headers=auth_headers, json={"name": "GG", "description": ""}
    )
    project_id = created.get_json()["id"]

    goal = client.post(
        f"/projects/{project_id}/goals",
        headers=auth_headers,
        json={"goal_text": "first goal"},
    )
    assert_that(goal.status_code).described_as("create goal status").is_equal_to(201)

    return project_id


def test_get_daily_goals_returns_list(client, auth_headers, project_with_goal):
    res = client.get(f"/projects/{project_with_goal}/goals", headers=auth_headers)
    assert_that(res.status_code).described_as("status").is_equal_to(200)
    assert_that(res.get_json()).described_as("response body").is_instance_of(list)


def test_get_daily_goals_includes_created_goal(client, auth_headers, project_with_goal):
    res = client.get(f"/projects/{project_with_goal}/goals", headers=auth_headers)
    texts = [g["goal_text"] for g in res.get_json()]
    assert_that(texts).described_as("goal texts").contains("first goal")


def test_get_daily_goals_project_not_found(client, auth_headers):
    res = client.get("/projects/999999/goals", headers=auth_headers)
    assert_that(res.status_code).described_as("status").is_equal_to(404)
    assert_that(res.get_json()["error"]).described_as("error message").is_equal_to("Project not found")

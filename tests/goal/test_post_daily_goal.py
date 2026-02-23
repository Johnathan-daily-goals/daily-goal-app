import pytest
from assertpy import assert_that


@pytest.fixture
def auth_headers(authenticated_user):
    return {"Authorization": f"Bearer {authenticated_user['access_token']}"}


@pytest.fixture
def created_project(client, auth_headers):
    res = client.post(
        "/projects", headers=auth_headers, json={"name": "G", "description": ""}
    )
    assert_that(res.status_code).described_as("create project status").is_equal_to(201)
    return res.get_json()["id"]


def test_create_daily_goal_success(client, auth_headers, created_project):
    res = client.post(
        f"/projects/{created_project}/goals",
        headers=auth_headers,
        json={"goal_text": "do the thing"},
    )
    assert_that(res.status_code).described_as("status").is_equal_to(201)
    body = res.get_json()
    assert_that(body).described_as("id field").contains_key("id")
    assert_that(body["project_id"]).described_as("project_id").is_equal_to(created_project)


def test_create_daily_goal_missing_goal_text(client, auth_headers, created_project):
    res = client.post(
        f"/projects/{created_project}/goals", headers=auth_headers, json={}
    )
    assert_that(res.status_code).described_as("status").is_equal_to(400)
    assert_that(res.get_json()["error"]).described_as("error message").is_equal_to("goal_text required")


def test_create_daily_goal_project_not_found(client, auth_headers):
    res = client.post(
        "/projects/999999/goals", headers=auth_headers, json={"goal_text": "x"}
    )
    assert_that(res.status_code).described_as("status").is_equal_to(404)
    assert_that(res.get_json()["error"]).described_as("error message").is_equal_to("Project not found")

import pytest
from assertpy import assert_that


@pytest.fixture
def auth_headers(authenticated_user):
    return {"Authorization": f"Bearer {authenticated_user['access_token']}"}


@pytest.fixture
def created_project(client, auth_headers):
    res = client.post(
        "/projects", headers=auth_headers, json={"name": "UPSERT", "description": ""}
    )
    assert_that(res.status_code).described_as("create project status").is_equal_to(201)
    return res.get_json()["id"]


def test_upsert_today_goal_creates(client, auth_headers, created_project):
    res = client.put(
        f"/projects/{created_project}/goals/today",
        headers=auth_headers,
        json={"goal_text": "first"},
    )
    assert_that(res.status_code).described_as("status").is_equal_to(201)
    assert_that(res.get_json()["goal_text"]).described_as("goal text").is_equal_to("first")


def test_upsert_today_goal_updates(client, auth_headers, created_project):
    first = client.put(
        f"/projects/{created_project}/goals/today",
        headers=auth_headers,
        json={"goal_text": "first"},
    )
    assert_that(first.status_code).described_as("initial upsert status").is_in(200, 201)

    second = client.put(
        f"/projects/{created_project}/goals/today",
        headers=auth_headers,
        json={"goal_text": "updated"},
    )
    assert_that(second.status_code).described_as("update status").is_equal_to(200)
    assert_that(second.get_json()["goal_text"]).described_as("updated goal text").is_equal_to("updated")


def test_upsert_today_goal_missing_goal_text(client, auth_headers, created_project):
    res = client.put(
        f"/projects/{created_project}/goals/today", headers=auth_headers, json={}
    )
    assert_that(res.status_code).described_as("status").is_equal_to(400)
    assert_that(res.get_json()["error"]).described_as("error message").is_equal_to("goal_text required")

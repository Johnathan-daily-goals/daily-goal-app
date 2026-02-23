import pytest
from assertpy import assert_that


@pytest.fixture
def auth_headers(authenticated_user):
    return {"Authorization": f"Bearer {authenticated_user['access_token']}"}


@pytest.fixture
def project(client, auth_headers, fake):
    res = client.post(
        "/projects",
        headers=auth_headers,
        json={"name": fake.word(), "description": fake.sentence()},
    )
    return res.get_json()


def test_patch_project_name(client, auth_headers, project, fake):
    new_name = fake.word()
    res = client.patch(
        f"/projects/{project['id']}",
        headers=auth_headers,
        json={"name": new_name},
    )
    assert_that(res.status_code).described_as("status").is_equal_to(200)
    assert_that(res.get_json()["name"]).described_as("updated name").is_equal_to(new_name)


def test_patch_project_description(client, auth_headers, project, fake):
    new_desc = fake.sentence()
    res = client.patch(
        f"/projects/{project['id']}",
        headers=auth_headers,
        json={"description": new_desc},
    )
    assert_that(res.status_code).described_as("status").is_equal_to(200)
    assert_that(res.get_json()["description"]).described_as("updated description").is_equal_to(new_desc)


def test_patch_project_name_and_description(client, auth_headers, project, fake):
    new_name = fake.word()
    new_desc = fake.sentence()
    res = client.patch(
        f"/projects/{project['id']}",
        headers=auth_headers,
        json={"name": new_name, "description": new_desc},
    )
    assert_that(res.status_code).described_as("status").is_equal_to(200)
    body = res.get_json()
    assert_that(body["name"]).described_as("updated name").is_equal_to(new_name)
    assert_that(body["description"]).described_as("updated description").is_equal_to(new_desc)


def test_patch_project_no_fields(client, auth_headers, project):
    res = client.patch(
        f"/projects/{project['id']}",
        headers=auth_headers,
        json={},
    )
    assert_that(res.status_code).described_as("status").is_equal_to(400)


def test_patch_project_not_found(client, auth_headers):
    res = client.patch(
        "/projects/999999",
        headers=auth_headers,
        json={"name": "x"},
    )
    assert_that(res.status_code).described_as("status").is_equal_to(404)


def test_patch_project_requires_auth(client, project):
    res = client.patch(f"/projects/{project['id']}", json={"name": "x"})
    assert_that(res.status_code).described_as("status").is_equal_to(401)

from assertpy import assert_that


def test_refresh_success_rotates_refresh_token(client, authenticated_user):
    old_refresh = authenticated_user["refresh_token"]

    res = client.post("/auth/refresh", json={"refresh_token": old_refresh})
    assert_that(res.status_code).described_as("status").is_equal_to(200)

    body = res.get_json()
    assert_that(body).described_as("response fields").contains_key("access_token", "refresh_token", "expires_at")
    assert_that(body["refresh_token"]).described_as("rotated refresh token").is_not_equal_to(old_refresh)


def test_refresh_missing_refresh_token(client):
    res = client.post("/auth/refresh", json={})
    assert_that(res.status_code).described_as("status").is_equal_to(400)
    assert_that(res.get_json()["error"]).described_as("error message").is_equal_to("refresh_token required")


def test_refresh_invalid_refresh_token(client):
    res = client.post("/auth/refresh", json={"refresh_token": "not-a-real-token"})
    assert_that(res.status_code).described_as("status").is_equal_to(401)
    assert_that(res.get_json()["error"]).described_as("error message").is_equal_to("Invalid or expired refresh token")

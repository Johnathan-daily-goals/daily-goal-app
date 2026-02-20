from assertpy import assert_that


def test_logout_success_revokes_tokens(client, authenticated_user):
    access_token = authenticated_user["access_token"]
    refresh_token = authenticated_user["refresh_token"]

    res = client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"refresh_token": refresh_token},
    )

    assert_that(res.status_code).described_as("status").is_equal_to(200)
    body = res.get_json()
    assert_that(body["status"]).described_as("logout status").is_equal_to("logged_out")
    assert_that(body).described_as("revocation fields").contains_key("refresh_token_revoked", "access_token_revoked")


def test_logout_missing_refresh_token(client, authenticated_user):
    res = client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {authenticated_user['access_token']}"},
        json={},
    )
    assert_that(res.status_code).described_as("status").is_equal_to(400)
    assert_that(res.get_json()["error"]).described_as("error message").is_equal_to("refresh_token required")


def test_logout_does_not_fail_if_refresh_token_already_revoked(client, authenticated_user):
    access_token = authenticated_user["access_token"]
    refresh_token = authenticated_user["refresh_token"]

    first = client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"refresh_token": refresh_token},
    )
    assert_that(first.status_code).described_as("first logout status").is_equal_to(200)

    second = client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"refresh_token": refresh_token},
    )
    assert_that(second.status_code).described_as("second logout status").is_equal_to(200)
    assert_that(second.get_json()["status"]).described_as("second logout body").is_equal_to("logged_out")

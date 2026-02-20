def test_logout_success_revokes_tokens(client, authenticated_user):
    access_token = authenticated_user["access_token"]
    refresh_token = authenticated_user["refresh_token"]

    res = client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"refresh_token": refresh_token},
    )

    assert res.status_code == 200
    body = res.get_json()
    assert body["status"] == "logged_out"
    assert "refresh_token_revoked" in body
    assert "access_token_revoked" in body


def test_logout_missing_refresh_token(client, authenticated_user):
    res = client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {authenticated_user['access_token']}"},
        json={},
    )
    assert res.status_code == 400
    assert res.get_json()["error"] == "refresh_token required"


def test_logout_does_not_fail_if_refresh_token_already_revoked(
    client, authenticated_user
):
    access_token = authenticated_user["access_token"]
    refresh_token = authenticated_user["refresh_token"]

    first = client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"refresh_token": refresh_token},
    )
    assert first.status_code == 200

    second = client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"refresh_token": refresh_token},
    )
    assert second.status_code == 200
    assert second.get_json()["status"] == "logged_out"

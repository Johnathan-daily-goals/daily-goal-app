def test_refresh_success_rotates_refresh_token(client, authenticated_user):
    old_refresh = authenticated_user["refresh_token"]

    res = client.post("/auth/refresh", json={"refresh_token": old_refresh})
    assert res.status_code == 200

    body = res.get_json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert "expires_at" in body
    assert body["refresh_token"] != old_refresh


def test_refresh_missing_refresh_token(client):
    res = client.post("/auth/refresh", json={})
    assert res.status_code == 400
    assert res.get_json()["error"] == "refresh_token required"


def test_refresh_invalid_refresh_token(client):
    res = client.post("/auth/refresh", json={"refresh_token": "not-a-real-token"})
    assert res.status_code == 401
    assert res.get_json()["error"] == "Invalid or expired refresh token"
def test_register_success(client, fake):
    email = fake.unique.email()
    password = fake.password(length=12)

    res = client.post("/auth/register", json={"email": email, "password": password})

    assert res.status_code == 201
    body = res.get_json()
    assert body["email"] == email
    assert "id" in body


def test_register_missing_fields(client):
    res = client.post("/auth/register", json={"email": "", "password": ""})
    assert res.status_code == 400
    assert res.get_json()["error"] == "email and password required"


def test_register_duplicate_email_conflict(client, fake):
    email = fake.unique.email()
    password = fake.password(length=12)

    first = client.post("/auth/register", json={"email": email, "password": password})
    assert first.status_code == 201

    second = client.post("/auth/register", json={"email": email, "password": password})
    assert second.status_code == 409
    assert second.get_json()["error"] == "Email already registered"
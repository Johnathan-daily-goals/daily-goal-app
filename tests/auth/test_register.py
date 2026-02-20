from assertpy import assert_that


def test_register_success(client, fake):
    email = fake.unique.email()
    password = fake.password(length=12)

    res = client.post("/auth/register", json={"email": email, "password": password})

    assert_that(res.status_code).described_as("status").is_equal_to(201)
    body = res.get_json()
    assert_that(body["email"]).described_as("email").is_equal_to(email)
    assert_that(body).described_as("id field").contains_key("id")


def test_register_missing_fields(client):
    res = client.post("/auth/register", json={"email": "", "password": ""})
    assert_that(res.status_code).described_as("status").is_equal_to(400)
    assert_that(res.get_json()["error"]).described_as("error message").is_equal_to("email and password required")


def test_register_duplicate_email_conflict(client, fake):
    email = fake.unique.email()
    password = fake.password(length=12)

    first = client.post("/auth/register", json={"email": email, "password": password})
    assert_that(first.status_code).described_as("first register status").is_equal_to(201)

    second = client.post("/auth/register", json={"email": email, "password": password})
    assert_that(second.status_code).described_as("duplicate register status").is_equal_to(409)
    assert_that(second.get_json()["error"]).described_as("error message").is_equal_to("Email already registered")

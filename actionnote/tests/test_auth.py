def register(client, username="alice", email="alice@example.com", password="password123"):
    return client.post(
        "/register",
        data={
            "username": username,
            "email": email,
            "password": password,
            "confirm_password": password,
            "full_name": "Alice",
        },
    )


def test_register_success_redirects_to_login(client):
    response = register(client)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_register_duplicate_username_rejected(client):
    register(client)
    response = register(client, email="other@example.com")
    assert response.status_code == 200
    assert b"already exists" in response.data


def test_register_duplicate_email_rejected(client):
    register(client)
    response = register(client, username="bob")
    assert response.status_code == 200
    assert b"already exists" in response.data


def test_register_weak_password_rejected(client):
    response = register(client, password="short")
    assert response.status_code == 200
    assert b"characters" in response.data


def test_login_success_redirects_to_dashboard(client):
    register(client)
    response = client.post("/login", data={"username": "alice", "password": "password123"})
    assert response.status_code == 302
    assert "/dashboard" in response.headers["Location"]


def test_login_wrong_password_rejected(client):
    register(client)
    response = client.post("/login", data={"username": "alice", "password": "wrong"})
    assert response.status_code == 200
    assert b"Invalid username or password" in response.data


def test_login_nonexistent_user_rejected(client):
    response = client.post("/login", data={"username": "ghost", "password": "password123"})
    assert response.status_code == 200
    assert b"Invalid username or password" in response.data


def test_logout_requires_login_then_clears_session(registered_client):
    response = registered_client.get("/logout")
    assert response.status_code == 302

    dashboard = registered_client.get("/dashboard")
    assert dashboard.status_code == 302
    assert "/login" in dashboard.headers["Location"]


def test_dashboard_requires_login(client):
    response = client.get("/dashboard")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]

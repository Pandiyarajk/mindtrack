import importlib

import pytest


@pytest.fixture
def app(tmp_path, monkeypatch):
    """A fresh Flask app per test, backed by an isolated data/ directory."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("FLASK_DEBUG", "false")
    monkeypatch.setenv("SCHEDULER_ENABLED", "false")

    import app as app_module

    importlib.reload(app_module)
    app_module.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    yield app_module.app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def registered_client(client):
    client.post(
        "/register",
        data={
            "username": "alice",
            "email": "alice@example.com",
            "password": "password123",
            "confirm_password": "password123",
            "full_name": "Alice",
        },
    )
    client.post("/login", data={"username": "alice", "password": "password123"})
    return client

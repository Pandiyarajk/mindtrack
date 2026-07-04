def test_api_config_returns_without_error(registered_client):
    response = registered_client.get("/api/config")
    assert response.status_code == 200
    data = response.get_json()
    assert set(data.keys()) == {
        "openai_enabled", "email_enabled", "notifications_enabled", "scheduler_enabled"
    }

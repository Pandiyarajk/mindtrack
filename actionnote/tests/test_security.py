def test_missing_csrf_token_returns_400_not_500(app, client):
    app.config['WTF_CSRF_ENABLED'] = True
    response = client.post(
        "/register",
        data={
            "username": "alice",
            "email": "alice@example.com",
            "password": "password123",
            "confirm_password": "password123",
            "full_name": "Alice",
        },
    )
    assert response.status_code == 400

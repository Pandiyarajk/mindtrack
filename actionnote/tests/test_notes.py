def create_note(client, text="Follow up with Raj about the proposal"):
    return client.post("/api/notes", json={"text": text})


def test_create_note_extracts_tasks_without_api_key(registered_client):
    response = create_note(registered_client)
    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is True
    assert data["tasks_created"] == 1
    assert data["note"]["text"] == "Follow up with Raj about the proposal"


def test_create_note_requires_text(registered_client):
    response = registered_client.post("/api/notes", json={"text": "  "})
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_get_notes_returns_created_note(registered_client):
    create_note(registered_client)
    response = registered_client.get("/api/notes")
    data = response.get_json()

    assert response.status_code == 200
    assert len(data["notes"]) == 1


def test_update_note_changes_text(registered_client):
    note = create_note(registered_client).get_json()["note"]
    response = registered_client.put(f"/api/notes/{note['id']}", json={"text": "Updated text"})
    assert response.status_code == 200

    notes = registered_client.get("/api/notes").get_json()["notes"]
    assert notes[0]["text"] == "Updated text"


def test_update_missing_note_returns_404(registered_client):
    response = registered_client.put("/api/notes/does-not-exist", json={"text": "x"})
    assert response.status_code == 404


def test_delete_note_removes_it(registered_client):
    note = create_note(registered_client).get_json()["note"]
    response = registered_client.delete(f"/api/notes/{note['id']}")
    assert response.status_code == 200

    notes = registered_client.get("/api/notes").get_json()["notes"]
    assert notes == []


def test_delete_missing_note_is_idempotent(registered_client):
    # note_handler.delete_note() filters by id and always reports success,
    # even when nothing matched -- deleting a missing note is a no-op, not a 404.
    response = registered_client.delete("/api/notes/does-not-exist")
    assert response.status_code == 200


def test_archive_note_moves_it_out_of_active_notes(registered_client):
    note = create_note(registered_client).get_json()["note"]
    response = registered_client.post(f"/api/notes/{note['id']}/archive")
    assert response.status_code == 200

    notes = registered_client.get("/api/notes").get_json()["notes"]
    assert notes == []


def test_notes_are_isolated_per_user(client):
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
    client.post(
        "/register",
        data={
            "username": "bob",
            "email": "bob@example.com",
            "password": "password123",
            "confirm_password": "password123",
            "full_name": "Bob",
        },
    )

    client.post("/login", data={"username": "alice", "password": "password123"})
    create_note(client, text="Alice's note")
    client.get("/logout")

    client.post("/login", data={"username": "bob", "password": "password123"})
    bob_notes = client.get("/api/notes").get_json()["notes"]
    assert bob_notes == []

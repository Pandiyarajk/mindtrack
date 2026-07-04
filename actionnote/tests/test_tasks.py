def create_note_with_task(client, text="Call the client urgently"):
    response = client.post("/api/notes", json={"text": text})
    note = response.get_json()["note"]
    return note, note["tasks"][0]


def test_get_tasks_aggregates_across_notes(registered_client):
    create_note_with_task(registered_client, "Call the client urgently")
    create_note_with_task(registered_client, "Email the report when possible")

    response = registered_client.get("/api/tasks")
    data = response.get_json()

    assert response.status_code == 200
    assert len(data["tasks"]) == 2


def test_update_task_fields(registered_client):
    _, task = create_note_with_task(registered_client)
    response = registered_client.put(f"/api/tasks/{task['id']}", json={"title": "Updated title"})
    assert response.status_code == 200

    tasks = registered_client.get("/api/tasks").get_json()["tasks"]
    assert tasks[0]["title"] == "Updated title"


def test_update_missing_task_returns_404(registered_client):
    response = registered_client.put("/api/tasks/does-not-exist", json={"title": "x"})
    assert response.status_code == 404


def test_update_task_status_valid_transition(registered_client):
    _, task = create_note_with_task(registered_client)
    response = registered_client.put(f"/api/tasks/{task['id']}/status", json={"status": "Done"})
    assert response.status_code == 200

    tasks = registered_client.get("/api/tasks").get_json()["tasks"]
    assert tasks[0]["status"] == "Done"


def test_update_task_status_rejects_invalid_status(registered_client):
    _, task = create_note_with_task(registered_client)
    response = registered_client.put(f"/api/tasks/{task['id']}/status", json={"status": "Cancelled"})
    assert response.status_code == 400


def test_update_status_for_missing_task_returns_404(registered_client):
    response = registered_client.put("/api/tasks/does-not-exist/status", json={"status": "Done"})
    assert response.status_code == 404

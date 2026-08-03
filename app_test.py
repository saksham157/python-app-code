"""Tests for the in-memory to-do list app."""

import app


def setup_function():
    """Reset the shared task list before every test.

    WHY: app.tasks is a module-level list, shared across all tests.
    Without resetting it, tests would leak state into each other —
    e.g. test_add_task adds a task, then test_list_tasks sees it too
    and gives a false pass/fail depending on run order.
    """
    app.tasks.clear()


def test_add_task():
    task = app.add_task("Write tests")
    assert task["title"] == "Write tests"
    assert task["completed"] is False
    assert task["id"] == 1


def test_add_task_increments_id():
    app.add_task("First")
    second = app.add_task("Second")
    assert second["id"] == 2


def test_list_tasks_empty():
    assert app.list_tasks() == []


def test_list_tasks_returns_added_tasks():
    app.add_task("Task A")
    app.add_task("Task B")
    assert len(app.list_tasks()) == 2


def test_complete_task_marks_completed():
    app.add_task("Finish report")
    result = app.complete_task(1)
    assert result is True
    assert app.tasks[0]["completed"] is True


def test_complete_task_missing_id_returns_false():
    app.add_task("Only task")
    result = app.complete_task(99)
    assert result is False


def test_remove_task():
    app.add_task("Delete me")
    result = app.remove_task(1)
    assert result is True
    assert app.list_tasks() == []


def test_remove_task_missing_id_returns_false():
    app.add_task("Keep me")
    result = app.remove_task(99)
    assert result is False
    assert len(app.list_tasks()) == 1


# --- New tests: Flask API layer ---

def setup_client():
    """Create a Flask test client for hitting routes without a real server."""
    app.app.config["TESTING"] = True
    return app.app.test_client()


def test_health_endpoint():
    client = setup_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "hello from jenkins shared pipeline"}


def test_get_tasks_endpoint():
    client = setup_client()
    app.add_task("Via API")
    response = client.get("/tasks")
    assert response.status_code == 200
    assert len(response.get_json()) == 1


def test_create_task_endpoint():
    client = setup_client()
    response = client.post("/tasks", json={"title": "New task"})
    assert response.status_code == 201
    assert response.get_json()["title"] == "New task"


def test_complete_task_endpoint():
    client = setup_client()
    app.add_task("Complete me")
    response = client.post("/tasks/1/complete")
    assert response.status_code == 200
    assert response.get_json()["success"] is True


def test_delete_task_endpoint():
    client = setup_client()
    app.add_task("Delete me via API")
    response = client.delete("/tasks/1")
    assert response.status_code == 200
    assert response.get_json()["success"] is True
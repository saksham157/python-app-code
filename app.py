"""Simple in-memory to-do list application with a REST API."""

from flask import Flask, jsonify, request

app = Flask(__name__)

tasks = []


def add_task(title):
    """Add a new task with a title, defaults to not completed."""
    task = {"id": len(tasks) + 1, "title": title, "completed": False}
    tasks.append(task)
    return task


def list_tasks():
    """Return all tasks currently stored."""
    return tasks


def complete_task(task_id):
    """Mark a task as completed by its id. Returns True if found."""
    for task in tasks:
        if task["id"] == task_id:
            task["completed"] = True
            return True
    return False


def remove_task(task_id):
    """Remove a task by its id. Returns True if it existed."""
    for task in tasks:
        if task["id"] == task_id:
            tasks.remove(task)
            return True
    return False


def print_tasks():
    """Print all tasks in a readable format."""
    if not tasks:
        print("No tasks yet.")
        return
    for task in tasks:
        status = "[x]" if task["completed"] else "[ ]"
        print(f"{status} {task['id']}: {task['title']}")


# --- Web layer: this is what keeps the container alive in Kubernetes ---

@app.route("/health")
def health():
    """Used by Kubernetes liveness/readiness probes."""
    return jsonify({"status": "hello from jenkins shared pipeline"})


@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify(list_tasks())


@app.route("/tasks", methods=["POST"])
def create_task():
    title = request.json.get("title")
    return jsonify(add_task(title)), 201


@app.route("/tasks/<int:task_id>/complete", methods=["POST"])
def mark_complete(task_id):
    success = complete_task(task_id)
    return jsonify({"success": success})


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    success = remove_task(task_id)
    return jsonify({"success": success})


def main():
    add_task("Learn Jenkins shared libraries")
    add_task("Set up ArgoCD")
    add_task("Understand SonarQube")
    complete_task(1)
    print_tasks()


if __name__ == "__main__":
    main()
    app.run(host="0.0.0.0", port=5000)
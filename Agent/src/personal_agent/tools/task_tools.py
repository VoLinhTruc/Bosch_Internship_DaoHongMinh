import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from personal_agent.config import BASE_DIR, MAX_READ_CHARS


TASKS_PATH = BASE_DIR / "data" / "tasks.json"
TASK_STATUSES = {"open", "in_progress", "blocked", "done", "cancelled"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_tasks() -> list[dict[str, Any]]:
    if not TASKS_PATH.exists():
        return []

    try:
        data = json.loads(TASKS_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []

    if isinstance(data, list):
        return [task for task in data if isinstance(task, dict)]

    return []


def _save_tasks(tasks: list[dict[str, Any]]) -> None:
    TASKS_PATH.parent.mkdir(parents=True, exist_ok=True)
    TASKS_PATH.write_text(json.dumps(tasks, indent=2), encoding="utf-8")


def add_task(
    title: str,
    details: str = "",
    due_date: str = "",
    priority: str = "normal",
) -> str:
    """
    Add a task to Agent/data/tasks.json.

    Args:
        title: Short task title.
        details: Optional task details.
        due_date: Optional ISO date or datetime.
        priority: Optional priority label such as low, normal, high, or urgent.
    """
    if not title or not title.strip():
        return "task title must not be empty."

    tasks = _load_tasks()
    task = {
        "id": uuid4().hex[:8],
        "title": title.strip(),
        "details": details,
        "due_date": due_date,
        "priority": priority or "normal",
        "status": "open",
        "created_at": _now(),
        "updated_at": _now(),
    }
    tasks.append(task)
    _save_tasks(tasks)
    return f"added task {task['id']}: {task['title']}"


def create_task(
    title: str,
    description: str = "",
    due_date: str = "",
    priority: str = "normal",
) -> str:
    """
    Create a local task.

    Args:
        title: Short task title.
        description: Optional task description.
        due_date: Optional ISO date or datetime.
        priority: Optional priority label such as low, normal, high, or urgent.
    """
    return add_task(
        title=title,
        details=description,
        due_date=due_date,
        priority=priority,
    )


def list_tasks(status: str = "open") -> str:
    """
    List tasks, optionally filtered by status.

    Args:
        status: Task status to show, or "all".
    """
    tasks = _load_tasks()
    if status != "all":
        tasks = [task for task in tasks if task.get("status") == status]

    if not tasks:
        return f"no tasks found for status: {status}"

    lines = []
    for task in tasks:
        due = f" due={task.get('due_date')}" if task.get("due_date") else ""
        lines.append(
            f"{task.get('id')} [{task.get('status')}] {task.get('title')} "
            f"(priority={task.get('priority', 'normal')}{due})"
        )

    result = "\n".join(lines)
    if len(result) > MAX_READ_CHARS:
        return result[:MAX_READ_CHARS] + "\n\n[TRUNCATED: too many tasks]"

    return result


def update_task(
    task_id: str,
    title: str = "",
    details: str = "",
    due_date: str = "",
    priority: str = "",
    status: str = "",
) -> str:
    """
    Update fields on an existing task.

    Args:
        task_id: Task id returned by add_task.
        title: Optional replacement title.
        details: Optional replacement details.
        due_date: Optional replacement due date.
        priority: Optional replacement priority.
        status: Optional replacement status.
    """
    tasks = _load_tasks()

    for task in tasks:
        if task.get("id") != task_id:
            continue

        if status and status not in TASK_STATUSES:
            return f"invalid task status: {status}. Valid statuses: {', '.join(sorted(TASK_STATUSES))}"

        if title:
            task["title"] = title.strip()
        if details:
            task["details"] = details
        if due_date:
            task["due_date"] = due_date
        if priority:
            task["priority"] = priority
        if status:
            task["status"] = status
        task["updated_at"] = _now()
        _save_tasks(tasks)
        return f"updated task {task_id}"

    return f"task not found: {task_id}"


def complete_task(task_id: str) -> str:
    """
    Mark a task as done.

    Args:
        task_id: Task id returned by add_task.
    """
    return update_task(task_id=task_id, status="done")

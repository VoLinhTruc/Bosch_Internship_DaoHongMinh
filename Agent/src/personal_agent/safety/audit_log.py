"""Simple audit log hooks for tool calls."""

from datetime import datetime, timezone

from personal_agent.config import BASE_DIR


AUDIT_LOG_PATH = BASE_DIR / "data" / "audit.log"


def record_event(event: str) -> None:
    """Append a timestamped audit event to Agent/data/audit.log."""
    AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat()
    with AUDIT_LOG_PATH.open("a", encoding="utf-8") as file:
        file.write(f"{timestamp} {event}\n")

"""Permission checks for higher-risk assistant actions."""


def requires_confirmation(action: str) -> bool:
    """Return whether an action should ask the user before running."""
    return action in {"delete_file", "send_email", "run_system_command"}

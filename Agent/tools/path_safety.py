from pathlib import Path

from config import WORKSPACE


def safe_path(path: str) -> Path:
    """
    Convert a relative path into a safe absolute path inside ./workspace.
    This prevents access to files outside the workspace folder.
    """
    if not path or path.strip() == "":
        path = "."

    target = (WORKSPACE / path).resolve()

    try:
        target.relative_to(WORKSPACE)
    except ValueError:
        raise ValueError("access denied: path is outside the workspace folder.")

    return target
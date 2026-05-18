import subprocess
from pathlib import Path

from personal_agent.config import BASE_DIR, MAX_READ_CHARS


def _repo_root() -> Path:
    completed = subprocess.run(
        ["git", "-C", str(BASE_DIR), "rev-parse", "--show-toplevel"],
        text=True,
        capture_output=True,
        timeout=10,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "not inside a git repository")
    return Path(completed.stdout.strip())


def _run_git(args: list[str]) -> str:
    root = _repo_root()
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        capture_output=True,
        timeout=20,
        check=False,
    )
    output = completed.stdout.strip()
    error = completed.stderr.strip()

    if completed.returncode != 0:
        return f"git command failed: {error or output}"

    result = output or "(no output)"
    if len(result) > MAX_READ_CHARS:
        return result[:MAX_READ_CHARS] + "\n\n[TRUNCATED: git output is too large]"

    return result


def git_status() -> str:
    """Return concise git working tree status."""
    return _run_git(["status", "--short"])


def git_diff(path: str = "") -> str:
    """
    Return the current unstaged git diff, optionally for one path.

    Args:
        path: Optional repository-relative path.
    """
    if path:
        return _run_git(["diff", "--", path])
    return _run_git(["diff"])


def git_log(limit: int = 5) -> str:
    """
    Return recent git commits.

    Args:
        limit: Number of commits to show, between 1 and 20.
    """
    count = min(max(limit, 1), 20)
    return _run_git(["log", f"-{count}", "--oneline", "--decorate"])

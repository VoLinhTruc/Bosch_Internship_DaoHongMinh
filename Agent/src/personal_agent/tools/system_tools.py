import os
import platform
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from personal_agent.config import BASE_DIR, WORKSPACE


def get_current_time(timezone_name: str = "") -> str:
    """
    Return the current time.

    Args:
        timezone_name: Optional IANA timezone name, such as UTC or Asia/Bangkok.
    """
    if timezone_name:
        try:
            now = datetime.now(ZoneInfo(timezone_name))
        except ZoneInfoNotFoundError:
            return f"unknown timezone: {timezone_name}"
    else:
        now = datetime.now().astimezone()

    return now.isoformat()


def get_system_info() -> str:
    """Return basic local runtime information."""
    return "\n".join(
        [
            f"platform: {platform.platform()}",
            f"python: {platform.python_version()}",
            f"machine: {platform.machine()}",
            f"processor: {platform.processor()}",
            f"cwd: {os.getcwd()}",
            f"agent_base_dir: {BASE_DIR}",
            f"workspace: {WORKSPACE}",
        ]
    )

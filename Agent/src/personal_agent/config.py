import json
from pathlib import Path
from typing import Any, cast

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*_args: object, **_kwargs: object) -> bool:
        return False


PACKAGE_DIR = Path(__file__).resolve().parent
BASE_DIR = PACKAGE_DIR.parents[1]

load_dotenv(BASE_DIR / ".env")

WORKSPACE = (BASE_DIR / "workspace").resolve()
WORKSPACE.mkdir(parents=True, exist_ok=True)

SETTINGS_PATH = BASE_DIR / "settings.json"

with SETTINGS_PATH.open("r", encoding="utf-8") as file:
    SETTINGS = cast(dict[str, Any], json.load(file))

PROVIDER = SETTINGS["provider"]
MODEL = SETTINGS["model"]
BASE_URL = SETTINGS.get("base_url")
API_KEY_ENV = SETTINGS.get("api_key_env")
TEMPERATURE = SETTINGS.get("temperature", 0.2)
MAX_TOOL_ROUNDS = SETTINGS.get("max_tool_rounds", 5)
OLLAMA_OPTIONS = cast(dict[str, Any], SETTINGS.get("ollama_options", {}))

MAX_READ_CHARS = SETTINGS["limits"]["max_read_chars"]
MAX_WRITE_CHARS = SETTINGS["limits"]["max_write_chars"]
MAX_APPEND_CHARS = SETTINGS["limits"]["max_append_chars"]
MAX_FILE_SIZE_CHARS = SETTINGS["limits"]["max_file_size_chars"]
MAX_MATCHES = SETTINGS["limits"]["max_matches"]
MAX_LINE_LENGTH = SETTINGS["limits"]["max_line_length"]

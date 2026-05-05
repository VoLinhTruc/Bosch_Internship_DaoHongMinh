import json
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
WORKSPACE = (BASE_DIR / "workspace").resolve()
WORKSPACE.mkdir(parents=True, exist_ok=True)

SETTINGS_PATH = BASE_DIR / "settings.json"

with SETTINGS_PATH.open("r", encoding="utf-8") as file:
    SETTINGS = json.load(file)

MODEL = SETTINGS["model"]

MAX_READ_CHARS = SETTINGS["limits"]["max_read_chars"]
MAX_WRITE_CHARS = SETTINGS["limits"]["max_write_chars"]
MAX_APPEND_CHARS = SETTINGS["limits"]["max_append_chars"]
MAX_FILE_SIZE_CHARS = SETTINGS["limits"]["max_file_size_chars"]
MAX_MATCHES = SETTINGS["limits"]["max_matches"]
MAX_LINE_LENGTH = SETTINGS["limits"]["max_line_length"]
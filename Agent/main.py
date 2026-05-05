from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()

MODEL = "gemini-3-flash-preview"

BASE_DIR = Path(__file__).resolve().parent
WORKSPACE = (BASE_DIR / "workspace").resolve()
#WORKSPACE.mkdir(parents=True, exist_ok=True)

### tools ###
# docstrings are important for LLM models to undertand what the tool does, when to call it and what args means

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


def list_files(path: str) -> str:
    """
    List files and folders inside the workspace.

    Args:
        path: Relative folder path inside the workspace. Use "." for the workspace root.
    """
    folder = safe_path(path)

    if not folder.exists():
        return f"folder does not exist: {path}"

    if not folder.is_dir():
        return f"path is not a folder: {path}"

    items = []

    for item in sorted(folder.iterdir()):
        kind = "DIR" if item.is_dir() else "FILE"
        relative_path = item.relative_to(WORKSPACE)
        items.append(f"[{kind}] {relative_path}")

    if not items:
        return "the folder is empty."

    return "\n".join(items)


def read_file(path: str) -> str:
    """
    Read a text file from the workspace.

    Args:
        path: Relative file path inside the workspace.
    """
    file_path = safe_path(path)

    if not file_path.exists():
        return f"file does not exist: {path}"

    if not file_path.is_file():
        return f"path is not a file: {path}"

    try:
        content = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return "could not read file as UTF-8 text."

    max_chars = 12000

    if len(content) > max_chars:
        return content[:max_chars] + "\n\n[TRUNCATED: file is too large]"

    return content


def write_file(path: str, content: str, overwrite: bool) -> str:
    """
    Write a text file inside the workspace.

    Args:
        path: Relative file path inside the workspace.
        content: Complete text content to write to the file.
        overwrite: Set to true only when the user explicitly wants to replace an existing file.
    """
    file_path = safe_path(path)

    if file_path.exists() and not overwrite:
        return (
            f"file already exists: {path}\n"
            "I did not overwrite it. Ask the user for permission or call write_file with overwrite=true only if the user clearly requested it."
        )

    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")

    relative_path = file_path.relative_to(WORKSPACE)
    return f"successfully wrote file: {relative_path}"


def append_file(path: str, content: str) -> str:
    """
    Append text content to a file inside the workspace.

    Args:
        path: Relative file path inside the workspace.
        content: Text content to add to the end of the file.
    """
    file_path = safe_path(path)

    if file_path.exists() and not file_path.is_file():
        return f"path is not a file: {path}"

    file_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with file_path.open("a", encoding="utf-8") as file:
            file.write(content)
    except UnicodeEncodeError:
        return "could not append content as UTF-8 text."

    relative_path = file_path.relative_to(WORKSPACE)
    return f"successfully appended to file: {relative_path}"


def search_files(keyword: str) -> str:
    """
    Search text files in the workspace for a keyword.

    Args:
        keyword: Text to search for inside files. The search is case-insensitive.
    """
    if not keyword or keyword.strip() == "":
        return "Keyword must not be empty."

    matches = []
    max_matches = 50
    lowered_keyword = keyword.lower()

    for file_path in sorted(path for path in WORKSPACE.rglob("*") if path.is_file()):
        try:
            relative_path = file_path.relative_to(WORKSPACE)
        except ValueError:
            continue

        try:
            lines = file_path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue

        for line_number, line in enumerate(lines, start=1):
            if lowered_keyword in line.lower():
                matches.append(f"{relative_path}:{line_number}: {line}")

                if len(matches) >= max_matches:
                    return "\n".join(matches) + "\n\n[TRUNCATED: too many matches]"

    if not matches:
        return f"no matches found for: {keyword}"

    return "\n".join(matches)


SYSTEM_INSTRUCTION = f"""
You are a local file assistant agent.

You can use tools to list, read, write, append, and search text files.

Important rules:
- You may only work inside this workspace folder: {WORKSPACE}
- Never claim you read a file unless you used read_file.
- Never claim you wrote or appended to a file unless write_file or append_file succeeded.
- Do not try to access files outside the workspace.
- If the user asks to update an existing file, read it first before writing changes.
- When writing a file, provide the complete final content.
- Use overwrite=false when creating new files.
- Use overwrite=true only when the user clearly asked to replace or update an existing file.
- After using tools, summarize what you did.
"""


def ask_agent(client: genai.Client, user_message: str) -> str:
    response = client.models.generate_content(
        model=MODEL,
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            tools=[list_files, read_file, write_file, append_file, search_files],
            temperature=0.2,
        ),
    )

    return response.text or "[no text response returned]"


def main() -> None:
    client = genai.Client()

    print(f"model: {MODEL}")
    print(f"workspace: {WORKSPACE}")
    print("type 'exit' to quit.\n")

    while True:
        user_message = input("You> ").strip()

        if user_message.lower() in {"exit", "quit"}:
            break

        if not user_message:
            continue

        try:
            answer = ask_agent(client, user_message)
        except Exception as error:
            answer = f"error: {type(error).__name__}: {error}"

        print("\nAgent>")
        print(answer)
        print()


if __name__ == "__main__":
    main()

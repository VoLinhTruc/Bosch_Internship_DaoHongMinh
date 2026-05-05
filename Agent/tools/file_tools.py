from config import (
    WORKSPACE,
    MAX_READ_CHARS,
    MAX_WRITE_CHARS,
    MAX_APPEND_CHARS,
    MAX_FILE_SIZE_CHARS,
    MAX_MATCHES,
    MAX_LINE_LENGTH,
)
from tools.path_safety import safe_path


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
    except OSError as error:
        return f"could not read file: {error}"

    if len(content) > MAX_READ_CHARS:
        return content[:MAX_READ_CHARS] + "\n\n[TRUNCATED: file is too large]"

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

    if len(content) > MAX_WRITE_CHARS:
        return (
            f"content is too large to write in one call. "
            f"limit is {MAX_WRITE_CHARS} characters."
        )

    if len(content) > MAX_FILE_SIZE_CHARS:
        return (
            f"file content is too large. "
            f"limit is {MAX_FILE_SIZE_CHARS} characters."
        )

    if file_path.exists() and not overwrite:
        return (
            f"file already exists: {path}\n"
            "I did not overwrite it. Ask the user for permission or call write_file with overwrite=true only if the user clearly requested it."
        )

    file_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        file_path.write_text(content, encoding="utf-8")
    except OSError as error:
        return f"could not write file: {error}"

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

    if len(content) > MAX_APPEND_CHARS:
        return (
            f"content is too large to append in one call. "
            f"limit is {MAX_APPEND_CHARS} characters."
        )

    if file_path.exists() and not file_path.is_file():
        return f"path is not a file: {path}"

    current_size = 0

    if file_path.exists():
        try:
            current_size = len(file_path.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            return "could not append because the existing file is not UTF-8 text."
        except OSError as error:
            return f"could not inspect existing file: {error}"

    if current_size + len(content) > MAX_FILE_SIZE_CHARS:
        return (
            f"append would make the file too large. "
            f"limit is {MAX_FILE_SIZE_CHARS} characters."
        )

    file_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with file_path.open("a", encoding="utf-8") as file:
            file.write(content)
    except UnicodeEncodeError:
        return "could not append content as UTF-8 text."
    except OSError as error:
        return f"could not append to file: {error}"

    relative_path = file_path.relative_to(WORKSPACE)
    return f"successfully appended to file: {relative_path}"


def search_files(keyword: str) -> str:
    """
    Search text files in the workspace for a keyword.

    Args:
        keyword: Text to search for inside files. The search is case-insensitive.
    """
    if not keyword or keyword.strip() == "":
        return "keyword must not be empty."

    matches = []
    lowered_keyword = keyword.lower()

    for file_path in sorted(WORKSPACE.rglob("*")):
        if not file_path.is_file():
            continue

        try:
            resolved_path = file_path.resolve()
            resolved_path.relative_to(WORKSPACE)
        except ValueError:
            continue

        try:
            with resolved_path.open("r", encoding="utf-8") as file:
                for line_number, line in enumerate(file, start=1):
                    line_without_newline = line.rstrip("\n")

                    if lowered_keyword in line_without_newline.lower():
                        if len(line_without_newline) > MAX_LINE_LENGTH:
                            shown_line = line_without_newline[:MAX_LINE_LENGTH] + "..."
                        else:
                            shown_line = line_without_newline

                        relative_path = resolved_path.relative_to(WORKSPACE)
                        matches.append(
                            f"{relative_path}:{line_number}: {shown_line}"
                        )

                        if len(matches) >= MAX_MATCHES:
                            return "\n".join(matches) + "\n\n[TRUNCATED: too many matches]"

        except UnicodeDecodeError:
            continue
        except OSError:
            continue

    if not matches:
        return f"no matches found for: {keyword}"

    return "\n".join(matches)
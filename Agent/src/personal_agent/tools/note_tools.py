import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

from personal_agent.config import BASE_DIR, MAX_READ_CHARS, MAX_WRITE_CHARS


NOTES_DIR = BASE_DIR / "data" / "notes"


def _slugify(title: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", title.strip()).strip("-._")
    if not slug:
        raise ValueError("title must contain at least one letter or number.")
    return slug[:80]


def _note_path(title: str) -> Path:
    return NOTES_DIR / f"{_slugify(title)}.md"


def _normalize_tags(tags: str) -> list[str]:
    return [
        tag.strip()
        for tag in tags.split(",")
        if tag.strip()
    ]


def _front_matter(title: str, tags: str = "") -> str:
    timestamp = datetime.now(timezone.utc).isoformat()
    normalized_tags = _normalize_tags(tags)
    tag_line = f"tags: {json.dumps(normalized_tags)}\n" if normalized_tags else ""
    return f"---\ntitle: {title}\n{tag_line}created_at: {timestamp}\n---\n\n"


def list_notes() -> str:
    """List saved notes."""
    if not NOTES_DIR.exists():
        return "no notes found."

    notes = sorted(NOTES_DIR.glob("*.md"))
    if not notes:
        return "no notes found."

    return "\n".join(note.stem for note in notes)


def create_note(title: str, content: str, overwrite: bool = False, tags: str = "") -> str:
    """
    Create or replace a note in Agent/data/notes.

    Args:
        title: Human-readable note title.
        content: Markdown note body.
        overwrite: Set true only when replacing an existing note.
        tags: Optional comma-separated tags.
    """
    if len(content) > MAX_WRITE_CHARS:
        return f"note content is too large. limit is {MAX_WRITE_CHARS} characters."

    path = _note_path(title)
    if path.exists() and not overwrite:
        return f"note already exists: {path.stem}. Use overwrite=true only if replacement was requested."

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_front_matter(title, tags) + content, encoding="utf-8")
    return f"saved note: {path.stem}"


def save_note(title: str, content: str, tags: str = "", overwrite: bool = False) -> str:
    """
    Save a tagged local Markdown note.

    Args:
        title: Human-readable note title.
        content: Markdown note body.
        tags: Optional comma-separated tags.
        overwrite: Set true only when replacing an existing note.
    """
    return create_note(title=title, content=content, overwrite=overwrite, tags=tags)


def read_note(title: str) -> str:
    """
    Read a saved note.

    Args:
        title: Note title or slug.
    """
    path = _note_path(title)
    if not path.exists():
        return f"note does not exist: {title}"

    content = path.read_text(encoding="utf-8")
    if len(content) > MAX_READ_CHARS:
        return content[:MAX_READ_CHARS] + "\n\n[TRUNCATED: note is too large]"

    return content


def search_notes(keyword: str) -> str:
    """
    Search saved notes for a case-insensitive keyword.

    Args:
        keyword: Text to search for.
    """
    if not keyword or not keyword.strip():
        return "keyword must not be empty."

    if not NOTES_DIR.exists():
        return "no notes found."

    matches: list[str] = []
    lowered_keyword = keyword.lower()

    for path in sorted(NOTES_DIR.glob("*.md")):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue

        for line_number, line in enumerate(lines, start=1):
            if lowered_keyword in line.lower():
                matches.append(f"{path.stem}:{line_number}: {line[:500]}")

    if not matches:
        return f"no note matches found for: {keyword}"

    return "\n".join(matches[:50])


def list_notes_json() -> list[dict[str, Any]]:
    """Return note metadata for internal callers that prefer structured data."""
    if not NOTES_DIR.exists():
        return []

    notes = []
    for path in sorted(NOTES_DIR.glob("*.md")):
        stat = path.stat()
        notes.append(
            {
                "slug": path.stem,
                "size": stat.st_size,
                "modified_at": datetime.fromtimestamp(
                    stat.st_mtime, timezone.utc
                ).isoformat(),
            }
        )
    return cast(list[dict[str, Any]], notes)

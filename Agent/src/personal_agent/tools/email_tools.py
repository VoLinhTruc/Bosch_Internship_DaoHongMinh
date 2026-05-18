import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from personal_agent.config import BASE_DIR, MAX_READ_CHARS, MAX_WRITE_CHARS


DRAFTS_PATH = BASE_DIR / "data" / "email_drafts.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_drafts() -> list[dict[str, Any]]:
    if not DRAFTS_PATH.exists():
        return []

    try:
        data = json.loads(DRAFTS_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []

    if isinstance(data, list):
        return [draft for draft in data if isinstance(draft, dict)]

    return []


def _save_drafts(drafts: list[dict[str, Any]]) -> None:
    DRAFTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    DRAFTS_PATH.write_text(json.dumps(drafts, indent=2), encoding="utf-8")


def create_email_draft(
    to: str,
    subject: str,
    body: str,
    cc: str = "",
    bcc: str = "",
) -> str:
    """
    Save an email draft locally. This tool does not send email.

    Args:
        to: Recipient email address or comma-separated addresses.
        subject: Email subject.
        body: Email body.
        cc: Optional comma-separated cc addresses.
        bcc: Optional comma-separated bcc addresses.
    """
    if not to or not to.strip():
        return "recipient must not be empty."
    if not subject or not subject.strip():
        return "subject must not be empty."
    if len(body) > MAX_WRITE_CHARS:
        return f"email body is too large. limit is {MAX_WRITE_CHARS} characters."

    drafts = _load_drafts()
    draft = {
        "id": uuid4().hex[:8],
        "to": to.strip(),
        "cc": cc.strip(),
        "bcc": bcc.strip(),
        "subject": subject.strip(),
        "body": body,
        "status": "draft",
        "created_at": _now(),
        "updated_at": _now(),
    }
    drafts.append(draft)
    _save_drafts(drafts)
    return f"saved email draft {draft['id']}: {draft['subject']}"


def list_email_drafts(status: str = "draft") -> str:
    """
    List locally saved email drafts.

    Args:
        status: Draft status to filter by, or "all".
    """
    drafts = _load_drafts()
    if status != "all":
        drafts = [draft for draft in drafts if draft.get("status") == status]

    if not drafts:
        return f"no email drafts found for status: {status}"

    lines = [
        f"{draft.get('id')} [{draft.get('status')}] to={draft.get('to')} subject={draft.get('subject')}"
        for draft in drafts
    ]
    return "\n".join(lines)


def read_email_draft(draft_id: str) -> str:
    """
    Read a locally saved email draft.

    Args:
        draft_id: Draft id returned by create_email_draft.
    """
    for draft in _load_drafts():
        if draft.get("id") != draft_id:
            continue

        content = json.dumps(draft, indent=2)
        if len(content) > MAX_READ_CHARS:
            return content[:MAX_READ_CHARS] + "\n\n[TRUNCATED: draft is too large]"
        return content

    return f"email draft not found: {draft_id}"


def update_email_draft(
    draft_id: str,
    to: str = "",
    subject: str = "",
    body: str = "",
    cc: str = "",
    bcc: str = "",
) -> str:
    """
    Update a locally saved email draft.

    Args:
        draft_id: Draft id returned by create_email_draft.
        to: Optional replacement recipient list.
        subject: Optional replacement subject.
        body: Optional replacement body.
        cc: Optional replacement cc list.
        bcc: Optional replacement bcc list.
    """
    if body and len(body) > MAX_WRITE_CHARS:
        return f"email body is too large. limit is {MAX_WRITE_CHARS} characters."

    drafts = _load_drafts()
    for draft in drafts:
        if draft.get("id") != draft_id:
            continue

        if to:
            draft["to"] = to.strip()
        if subject:
            draft["subject"] = subject.strip()
        if body:
            draft["body"] = body
        if cc:
            draft["cc"] = cc.strip()
        if bcc:
            draft["bcc"] = bcc.strip()
        draft["updated_at"] = _now()
        _save_drafts(drafts)
        return f"updated email draft {draft_id}"

    return f"email draft not found: {draft_id}"


def mark_email_draft_sent(draft_id: str) -> str:
    """
    Mark a locally saved email draft as sent. This does not send email.

    Args:
        draft_id: Draft id returned by create_email_draft.
    """
    drafts = _load_drafts()
    for draft in drafts:
        if draft.get("id") != draft_id:
            continue

        draft["status"] = "sent"
        draft["sent_at"] = _now()
        draft["updated_at"] = _now()
        _save_drafts(drafts)
        return f"marked email draft {draft_id} as sent"

    return f"email draft not found: {draft_id}"

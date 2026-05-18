from typing import Any


def _tool(
    name: str,
    description: str,
    properties: dict[str, dict[str, Any]],
    required: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required or [],
                "additionalProperties": False,
            },
        },
    }


STRING = {"type": "string"}


OPENAI_TOOLS = [
    _tool(
        "list_files",
        "List files and folders inside the workspace.",
        {
            "path": {
                "type": "string",
                "description": "Relative folder path inside the workspace. Use . for the workspace root.",
            }
        },
        ["path"],
    ),
    _tool(
        "read_file",
        "Read a UTF-8 text file from the workspace.",
        {"path": {"type": "string", "description": "Relative file path inside the workspace."}},
        ["path"],
    ),
    _tool(
        "read_file_window",
        "Read a numbered line window from a UTF-8 text file in the workspace.",
        {
            "path": {"type": "string", "description": "Relative file path inside the workspace."},
            "start_line": {"type": "integer", "description": "One-based line number where reading starts."},
            "line_count": {"type": "integer", "description": "Number of lines to return."},
        },
        ["path", "start_line", "line_count"],
    ),
    _tool(
        "write_file",
        "Write complete UTF-8 text content to a file inside the workspace.",
        {
            "path": {"type": "string", "description": "Relative file path inside the workspace."},
            "content": {"type": "string", "description": "Complete text content to write."},
            "overwrite": {
                "type": "boolean",
                "description": "True only when the user explicitly wants to replace an existing file.",
            },
        },
        ["path", "content", "overwrite"],
    ),
    _tool(
        "replace_text",
        "Replace exact text in a UTF-8 workspace file only when the occurrence count matches.",
        {
            "path": {"type": "string", "description": "Relative file path inside the workspace."},
            "old_text": {"type": "string", "description": "Exact text to replace."},
            "new_text": {"type": "string", "description": "Replacement text."},
            "expected_replacements": {
                "type": "integer",
                "description": "Expected number of occurrences to replace. Defaults to 1.",
            },
        },
        ["path", "old_text", "new_text"],
    ),
    _tool(
        "append_file",
        "Append UTF-8 text content to a file inside the workspace.",
        {
            "path": {"type": "string", "description": "Relative file path inside the workspace."},
            "content": {"type": "string", "description": "Text content to append."},
        },
        ["path", "content"],
    ),
    _tool(
        "search_files",
        "Search UTF-8 text files in the workspace for a case-insensitive keyword.",
        {"keyword": {"type": "string", "description": "Text to search for inside files."}},
        ["keyword"],
    ),
    _tool(
        "create_note",
        "Create or replace a local Markdown note.",
        {
            "title": {"type": "string", "description": "Human-readable note title."},
            "content": {"type": "string", "description": "Markdown note body."},
            "overwrite": {"type": "boolean", "description": "True only when replacing an existing note."},
            "tags": {"type": "string", "description": "Optional comma-separated tags."},
        },
        ["title", "content"],
    ),
    _tool(
        "save_note",
        "Save a tagged local Markdown note.",
        {
            "title": {"type": "string", "description": "Human-readable note title."},
            "content": {"type": "string", "description": "Markdown note body."},
            "tags": {"type": "string", "description": "Optional comma-separated tags."},
            "overwrite": {"type": "boolean", "description": "True only when replacing an existing note."},
        },
        ["title", "content"],
    ),
    _tool("list_notes", "List saved local notes.", {}),
    _tool(
        "read_note",
        "Read a saved local note.",
        {"title": {"type": "string", "description": "Note title or slug."}},
        ["title"],
    ),
    _tool(
        "search_notes",
        "Search saved notes for a case-insensitive keyword.",
        {"keyword": {"type": "string", "description": "Text to search for."}},
        ["keyword"],
    ),
    _tool(
        "add_task",
        "Add a local task.",
        {
            "title": {"type": "string", "description": "Short task title."},
            "details": {"type": "string", "description": "Optional task details."},
            "due_date": {"type": "string", "description": "Optional ISO date or datetime."},
            "priority": {"type": "string", "description": "Optional priority label."},
        },
        ["title"],
    ),
    _tool(
        "create_task",
        "Create a local task.",
        {
            "title": {"type": "string", "description": "Short task title."},
            "description": {"type": "string", "description": "Optional task description."},
            "due_date": {"type": "string", "description": "Optional ISO date or datetime."},
            "priority": {"type": "string", "description": "Optional priority label."},
        },
        ["title"],
    ),
    _tool(
        "list_tasks",
        "List local tasks, optionally filtered by status.",
        {"status": {"type": "string", "description": "Status to show, or all."}},
    ),
    _tool(
        "update_task",
        "Update fields on an existing local task.",
        {
            "task_id": {"type": "string", "description": "Task id."},
            "title": STRING,
            "details": STRING,
            "due_date": STRING,
            "priority": STRING,
            "status": {"type": "string", "description": "open, in_progress, blocked, done, or cancelled."},
        },
        ["task_id"],
    ),
    _tool(
        "complete_task",
        "Mark a local task as done.",
        {"task_id": {"type": "string", "description": "Task id."}},
        ["task_id"],
    ),
    _tool(
        "add_calendar_event",
        "Add a local calendar event.",
        {
            "title": STRING,
            "start": {"type": "string", "description": "Start date or datetime, ideally ISO formatted."},
            "end": {"type": "string", "description": "Optional end date or datetime."},
            "location": STRING,
            "notes": STRING,
        },
        ["title", "start"],
    ),
    _tool(
        "list_calendar_events",
        "List local calendar events with optional date filtering.",
        {
            "from_date": STRING,
            "to_date": STRING,
            "include_cancelled": {"type": "boolean"},
        },
    ),
    _tool(
        "update_calendar_event",
        "Update a local calendar event.",
        {
            "event_id": {"type": "string", "description": "Event id."},
            "title": STRING,
            "start": STRING,
            "end": STRING,
            "location": STRING,
            "notes": STRING,
        },
        ["event_id"],
    ),
    _tool(
        "cancel_calendar_event",
        "Mark a local calendar event as cancelled.",
        {"event_id": {"type": "string", "description": "Event id."}},
        ["event_id"],
    ),
    _tool(
        "create_email_draft",
        "Save a local email draft. This does not send email.",
        {
            "to": STRING,
            "subject": STRING,
            "body": STRING,
            "cc": STRING,
            "bcc": STRING,
        },
        ["to", "subject", "body"],
    ),
    _tool(
        "list_email_drafts",
        "List locally saved email drafts.",
        {"status": {"type": "string", "description": "Draft status to filter by, or all."}},
    ),
    _tool(
        "read_email_draft",
        "Read a locally saved email draft.",
        {"draft_id": {"type": "string", "description": "Draft id."}},
        ["draft_id"],
    ),
    _tool(
        "update_email_draft",
        "Update a locally saved email draft.",
        {
            "draft_id": {"type": "string", "description": "Draft id."},
            "to": STRING,
            "subject": STRING,
            "body": STRING,
            "cc": STRING,
            "bcc": STRING,
        },
        ["draft_id"],
    ),
    _tool(
        "mark_email_draft_sent",
        "Mark a local email draft as sent. This does not send email.",
        {"draft_id": {"type": "string", "description": "Draft id."}},
        ["draft_id"],
    ),
    _tool(
        "fetch_url",
        "Fetch a public http or https URL and return readable page text.",
        {
            "url": {"type": "string", "description": "Full URL beginning with http:// or https://."},
            "max_chars": {"type": "integer", "description": "Maximum characters to return."},
        },
        ["url"],
    ),
    _tool("git_status", "Return concise git working tree status.", {}),
    _tool(
        "git_diff",
        "Return the current unstaged git diff, optionally for one path.",
        {"path": {"type": "string", "description": "Optional repository-relative path."}},
    ),
    _tool(
        "git_log",
        "Return recent git commits.",
        {"limit": {"type": "integer", "description": "Number of commits to show, between 1 and 20."}},
    ),
    _tool(
        "get_current_time",
        "Return the current time.",
        {"timezone_name": {"type": "string", "description": "Optional IANA timezone name."}},
    ),
    _tool("get_system_info", "Return basic local runtime information.", {}),
]

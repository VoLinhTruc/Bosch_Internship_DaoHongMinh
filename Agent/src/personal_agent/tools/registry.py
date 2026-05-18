from personal_agent.tools.browser_tools import fetch_url
from personal_agent.tools.calendar_tools import (
    add_calendar_event,
    cancel_calendar_event,
    list_calendar_events,
    update_calendar_event,
)
from personal_agent.tools.email_tools import (
    create_email_draft,
    list_email_drafts,
    mark_email_draft_sent,
    read_email_draft,
    update_email_draft,
)
from personal_agent.tools.file_tools import (
    append_file,
    list_files,
    read_file,
    read_file_window,
    replace_text,
    search_files,
    write_file,
)
from personal_agent.tools.git_tools import git_diff, git_log, git_status
from personal_agent.tools.note_tools import create_note, list_notes, read_note, save_note, search_notes
from personal_agent.tools.system_tools import get_current_time, get_system_info
from personal_agent.tools.task_tools import add_task, complete_task, create_task, list_tasks, update_task


TOOL_REGISTRY = {
    "list_files": list_files,
    "read_file": read_file,
    "read_file_window": read_file_window,
    "write_file": write_file,
    "replace_text": replace_text,
    "append_file": append_file,
    "search_files": search_files,
    "create_note": create_note,
    "save_note": save_note,
    "list_notes": list_notes,
    "read_note": read_note,
    "search_notes": search_notes,
    "add_task": add_task,
    "create_task": create_task,
    "list_tasks": list_tasks,
    "update_task": update_task,
    "complete_task": complete_task,
    "add_calendar_event": add_calendar_event,
    "list_calendar_events": list_calendar_events,
    "update_calendar_event": update_calendar_event,
    "cancel_calendar_event": cancel_calendar_event,
    "create_email_draft": create_email_draft,
    "list_email_drafts": list_email_drafts,
    "read_email_draft": read_email_draft,
    "update_email_draft": update_email_draft,
    "mark_email_draft_sent": mark_email_draft_sent,
    "fetch_url": fetch_url,
    "git_status": git_status,
    "git_diff": git_diff,
    "git_log": git_log,
    "get_current_time": get_current_time,
    "get_system_info": get_system_info,
}

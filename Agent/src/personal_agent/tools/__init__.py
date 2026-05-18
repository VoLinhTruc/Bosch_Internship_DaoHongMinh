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
    list_files,
    read_file,
    read_file_window,
    write_file,
    replace_text,
    append_file,
    search_files,
)
from personal_agent.tools.git_tools import git_diff, git_log, git_status
from personal_agent.tools.note_tools import create_note, list_notes, read_note, save_note, search_notes
from personal_agent.tools.system_tools import get_current_time, get_system_info
from personal_agent.tools.task_tools import add_task, complete_task, create_task, list_tasks, update_task


AGENT_TOOLS = [
    list_files,
    read_file,
    read_file_window,
    write_file,
    replace_text,
    append_file,
    search_files,
    create_note,
    save_note,
    list_notes,
    read_note,
    search_notes,
    add_task,
    create_task,
    list_tasks,
    update_task,
    complete_task,
    add_calendar_event,
    list_calendar_events,
    update_calendar_event,
    cancel_calendar_event,
    create_email_draft,
    list_email_drafts,
    read_email_draft,
    update_email_draft,
    mark_email_draft_sent,
    fetch_url,
    git_status,
    git_diff,
    git_log,
    get_current_time,
    get_system_info,
]

FILE_TOOLS = AGENT_TOOLS

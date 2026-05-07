from tools.file_tools import (
    append_file,
    list_files,
    read_file,
    search_files,
    write_file,
)


TOOL_REGISTRY = {
    "list_files": list_files,
    "read_file": read_file,
    "write_file": write_file,
    "append_file": append_file,
    "search_files": search_files,
}

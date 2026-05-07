OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files and folders inside the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative folder path inside the workspace. Use . for the workspace root.",
                    }
                },
                "required": ["path"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a UTF-8 text file from the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative file path inside the workspace.",
                    }
                },
                "required": ["path"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write complete UTF-8 text content to a file inside the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative file path inside the workspace.",
                    },
                    "content": {
                        "type": "string",
                        "description": "Complete text content to write to the file.",
                    },
                    "overwrite": {
                        "type": "boolean",
                        "description": "Set to true only when the user explicitly wants to replace an existing file.",
                    },
                },
                "required": ["path", "content", "overwrite"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "append_file",
            "description": "Append UTF-8 text content to a file inside the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative file path inside the workspace.",
                    },
                    "content": {
                        "type": "string",
                        "description": "Text content to add to the end of the file.",
                    },
                },
                "required": ["path", "content"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_files",
            "description": "Search UTF-8 text files in the workspace for a case-insensitive keyword.",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "Text to search for inside files.",
                    }
                },
                "required": ["keyword"],
                "additionalProperties": False,
            },
        },
    },
]

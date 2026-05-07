Architecture and Tools
======================

Main Components
---------------

``main.py``
    creates the configured provider, prints the active provider, model, and
    workspace path, then loops over user messages until the user types ``exit``
    or ``quit``.

``agent.py``
    contains the provider-independent ``Agent`` wrapper. It delegates user
    messages to the selected provider.

``provider/``
    contains model API adapters. ``gemini_provider.py`` uses the Google Gemini
    SDK. ``openai_compatible_provider.py`` uses the OpenAI chat-completions
    interface and can be pointed at OpenAI-compatible local servers such as LM
    Studio or Ollama. ``ollama_provider.py`` uses Ollama's native ``/api/chat``
    endpoint.

``config.py``
    loads environment variables with ``python-dotenv``, defines project paths,
    creates the workspace folder when needed, and reads runtime settings from
    ``settings.json``.

``prompts.py``
    defines the system instruction given to the model. The prompt explains the
    agent role, lists important file-operation rules, and embeds the resolved
    workspace path so the model knows its allowed boundary.

``settings.json``
    Stores provider selection, model selection, local API base URL, API key
    environment variable name, generation options, and tool limits.

``tools/__init__.py``
    Imports the individual tool functions and exposes them as ``FILE_TOOLS`` for
    providers that accept Python callables directly.

``tools/registry.py``
    Maps portable tool names to Python functions so provider adapters can
    execute structured tool calls.

``tools/schemas.py``
    Defines OpenAI-compatible JSON tool schemas for providers that require
    function declarations.

``tools/file_tools.py``
    Implements the model-callable file operations.

``tools/path_safety.py``
    Provides ``safe_path()``, the central workspace-boundary check used by the
    file tools.

Runtime Flow
------------

1. ``python main.py`` starts the command-line interface.
2. ``main()`` creates the configured provider with ``provider.create_provider()``.
3. the user enters a message at the ``You>`` prompt.
4. ``main()`` passes the message to ``Agent.ask()``.
5. ``Agent.ask()`` delegates to the configured provider.
6. The provider sends the message, system instruction, and tool declarations to
   the selected model API.
7. The model may answer directly or call one of the registered file tools.
8. tool functions validate paths and limits, perform the requested file
   operation, and return a text result to the model.
9. ``main()`` prints the final response under the ``Agent>`` prompt.

Tool Architecture
-----------------

The agent exposes five file tools:

``list_files(path)``
    Lists files and folders under a relative path inside ``workspace``. It
    returns one line per entry, prefixed with ``[DIR]`` or ``[FILE]``.

``read_file(path)``
    Reads a UTF-8 text file from ``workspace``. If the file is larger than
    ``MAX_READ_CHARS``, the returned text is truncated and marked as truncated.

``write_file(path, content, overwrite)``
    Writes complete UTF-8 text content to a file inside ``workspace``. It
    refuses to overwrite existing files unless ``overwrite`` is true, and it
    enforces both per-write and total file-size limits.

``append_file(path, content)``
    appends UTF-8 text to a file inside ``workspace``. It checks the append
    size, rejects non-file targets, verifies existing text encoding, and
    prevents the resulting file from exceeding the configured maximum file
    size.

``search_files(keyword)``
    searches all UTF-8 text files in ``workspace`` for a case-insensitive
    keyword. Skips unreadable or non-UTF-8 files, caps the number of matches,
    and truncates long matching lines.

Safety Model
------------

safe guard for working environment is ``safe_path()`` in ``tools/path_safety.py``. It
combines the requested relative path with ``WORKSPACE``, resolves the result,
and verifies that the resolved path is still inside ``WORKSPACE``. If the path
escapes the workspace, the function raises ``ValueError``.

this protects against path traversal attempts such as ``..`` segments pointing
outside the allowed directory.

the workspace path is ``Agent/workspace``. ``config.py`` resolves this path and
creates it automatically if it does not already exist.

the file tools add further protections:

* text files are read and written as UTF-8
* read, write, append, search, and line-display sizes are limited by
  ``settings.json``
* write operations require explicit overwrite permission
* searches ignore directories and unreadable files

Configuration
-------------

The runtime configuration is split between environment variables and
``settings.json``.

Environment
    The Gemini API key is expected in ``.env`` as ``KEY``. The
    ``load_dotenv()`` call in ``config.py`` loads it before the client is used.

Settings file
    ``settings.json`` controls the model and tool limits. The ``safety`` block
    documents the intended policy, while the active boundary enforcement is
    implemented in ``safe_path()`` and the individual tool functions.

Extension Points
----------------

To add another tool:

1. implement a function with a clear docstring in ``tools/file_tools.py`` or a
   new module under ``tools``.
2. use ``safe_path()`` for any path that touches the filesystem.
3. enforce any size, encoding, or overwrite limits needed by the operation.
4. import the function in ``tools/__init__.py``.
5. add it to the ``FILE_TOOLS`` list.
6. update ``prompts.py`` if the model needs new behavioral rules.

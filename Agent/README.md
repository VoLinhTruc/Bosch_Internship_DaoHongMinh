# Personal Agent

Local personal assistant scaffold with provider support, workspace-safe file
tools, local productivity tools, URL fetching, git inspection, and safety hooks.

## Layout

```text
Agent/
├── main.py
├── src/personal_agent/
│   ├── agent.py
│   ├── config.py
│   ├── prompts.py
│   ├── memory/
│   ├── providers/
│   ├── tools/
│   └── safety/
├── docs/
├── data/
├── workspace/
└── settings.json
```

The active file tools are scoped to `./workspace`. Notes, tasks, calendar
events, and email drafts are stored locally under `./data`; email tools only
manage drafts and never send real email. Browser fetching is limited to public
HTTP(S) URLs, and git tools are read-only inspection helpers.

Implemented next-stage tools include line-window file reads, exact text
replacement, tagged notes, and task creation/listing/updating for a more
OpenClaw-style personal assistant foundation.

## Setup

From the `Agent` folder:

```powershell
.venv\Scripts\activate       
python -m pip install -r requirements.txt

python3 -m pip install -r requirements.txt
```

Add API key to `.env`:

```text
KEY=key
```

## Provider Settings

`settings.json` selects the provider and model.

The project is currently configured for LM Studio:

```json
{
  "provider": "lm_studio",
  "model": "auto",
  "base_url": "http://localhost:1234/v1",
  "api_key_env": "LM_STUDIO_API_KEY"
}
```

`model: "auto"` asks LM Studio for loaded models and chooses the first chat
model it sees. To pin one of your local models, start the LM Studio local
server, load the model, then run:

```bash
python scripts/list_lm_studio_models.py
```

Copy the exact model id into `settings.json`. The local models you downloaded
can be used this way:

| Use case | Recommended local model |
| --- | --- |
| Best coding agent behavior | Qwen3 Coder 30B |
| Strong general assistant | Gemma 4 31B |
| Faster general use | Qwen3.5 9B or Meta Llama 3.1 8B Instruct |
| Lighter fallback | Qwen2.5 7B Instruct or Gemma 4 E4B |
| Embeddings/search memory | Nomic Embed Text v1.5 |

If a loaded local model rejects tool schemas, set `"use_tools": false` in
`settings.json`. The agent will still chat, but it will not be able to call the
workspace, note, task, calendar, email draft, URL, git, or system tools.

For LM Studio running on another device through Link LM, put the remote
OpenAI-compatible URL in `.env`:

```text
LM_STUDIO_BASE_URL=http://REMOTE_DEVICE_OR_LINK_HOST:1234/v1
LM_STUDIO_API_KEY=local-api-key
```

The agent and helper scripts use `LM_STUDIO_BASE_URL` when it is set.

Gemini:

```json
{
  "provider": "gemini",
  "model": "gemini-3-flash-preview",
  "base_url": null,
  "api_key_env": "KEY"
}
```

LM Studio:

```json
{
  "provider": "lm_studio",
  "model": "auto",
  "base_url": "http://localhost:1234/v1",
  "api_key_env": "LM_STUDIO_API_KEY"
}
```

Ollama OpenAI-compatible endpoint:

```json
{
  "provider": "openai_compatible",
  "model": "llama3.1",
  "base_url": "http://localhost:11434/v1",
  "api_key_env": "OLLAMA_API_KEY"
}
```

Ollama native endpoint:

```json
{
  "provider": "ollama",
  "model": "llama3.1",
  "base_url": "http://localhost:11434",
  "api_key_env": null,
  "ollama_options": {}
}
```

For local providers, the API key can usually be any placeholder value if the
server does not enforce authentication.

To check the downloaded embedding model through LM Studio, load Nomic Embed
Text v1.5 in LM Studio and run:

```bash
python scripts/test_lm_studio_embedding.py "Remember that Bosch internship notes live in the workspace."
```

If LM Studio reports a different embedding model id, set it first:

```bash
export LM_STUDIO_EMBEDDING_MODEL="exact-model-id-from-lm-studio"
```

## Run

With the virtual environment activated:

```powershell
python main.py
```

If Gemini fails with `cannot import name 'genai' from 'google'`, install the
requirements in the same environment used to run `main.py`:

```bash
python -m pip install -r requirements.txt
```

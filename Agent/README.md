# Provider File Agent

AI agent to read and write files in `./workspace`.

## Setup

From the `Agent` folder:

```powershell
.venv\Scripts\activate       
python -m pip install -r requirements.txt
```

Add API key to `.env`:

```text
KEY=key
```

## Provider Settings

`settings.json` selects the provider and model.

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
  "provider": "openai_compatible",
  "model": "local-model",
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

## Run

With the virtual environment activated:

```powershell
python main.py
```

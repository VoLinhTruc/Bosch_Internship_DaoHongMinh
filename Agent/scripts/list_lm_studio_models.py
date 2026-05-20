from __future__ import annotations

import os
from pathlib import Path

from openai import APIConnectionError, OpenAI, OpenAIError
from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[1] / ".env")

BASE_URL = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")
API_KEY = os.getenv("LM_STUDIO_API_KEY", "local-api-key")


def main() -> None:
    client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
    try:
        models = client.models.list()
    except APIConnectionError:
        print(f"Could not connect to LM Studio at {BASE_URL}.")
        print("Start LM Studio's local server and load a model, then try again.")
        return
    except OpenAIError as error:
        print(f"LM Studio model list failed: {error}")
        return

    if not models.data:
        print("No models returned. Load a model in LM Studio first.")
        return

    for model in models.data:
        print(model.id)


if __name__ == "__main__":
    main()

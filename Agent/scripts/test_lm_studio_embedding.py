from __future__ import annotations

import os
from pathlib import Path
import sys

from openai import APIConnectionError, OpenAI, OpenAIError
from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[1] / ".env")

BASE_URL = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")
API_KEY = os.getenv("LM_STUDIO_API_KEY", "local-api-key")
EMBEDDING_MODEL = os.getenv("LM_STUDIO_EMBEDDING_MODEL", "nomic-embed-text-v1.5")


def main() -> None:
    text = " ".join(sys.argv[1:]) or "Test embedding from LM Studio."
    client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
    try:
        response = client.embeddings.create(model=EMBEDDING_MODEL, input=text)
    except APIConnectionError:
        print(f"Could not connect to LM Studio at {BASE_URL}.")
        print("Start LM Studio's local server and load the embedding model, then try again.")
        return
    except OpenAIError as error:
        print(f"LM Studio embedding request failed: {error}")
        return

    vector = response.data[0].embedding

    print(f"model: {EMBEDDING_MODEL}")
    print(f"dimensions: {len(vector)}")
    print(f"first_8_values: {vector[:8]}")


if __name__ == "__main__":
    main()

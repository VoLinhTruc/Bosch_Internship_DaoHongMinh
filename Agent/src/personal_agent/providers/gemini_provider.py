import os

from google import genai
from google.genai import types

from personal_agent.config import API_KEY_ENV, MODEL, TEMPERATURE
from personal_agent.prompts import SYSTEM_INSTRUCTION
from personal_agent.tools import FILE_TOOLS

from personal_agent.providers.base import AIProvider


class GeminiProvider(AIProvider):
    def __init__(self) -> None:
        api_key = os.getenv(API_KEY_ENV or "")
        if API_KEY_ENV and not api_key:
            raise ValueError(f"missing API key environment variable: {API_KEY_ENV}")

        self.client = genai.Client(api_key=api_key) if api_key else genai.Client()

    def ask(self, user_message: str) -> str:
        response = self.client.models.generate_content(
            model=MODEL,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                tools=FILE_TOOLS,
                temperature=TEMPERATURE,
            ),
        )

        return response.text or "[no text response returned]"

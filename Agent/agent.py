from google import genai
from google.genai import types

from config import MODEL
from prompts import SYSTEM_INSTRUCTION
from tools import FILE_TOOLS


def ask_agent(client: genai.Client, user_message: str) -> str:
    response = client.models.generate_content(
        model=MODEL,
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            tools=FILE_TOOLS,
            temperature=0.2,
        ),
    )

    return response.text or "[no text response returned]"
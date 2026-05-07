import json
import os
from typing import Any, cast

from openai import OpenAI

from config import API_KEY_ENV, BASE_URL, MAX_TOOL_ROUNDS, MODEL, TEMPERATURE
from prompts import SYSTEM_INSTRUCTION
from tools.registry import TOOL_REGISTRY
from tools.schemas import OPENAI_TOOLS

from provider.base import AIProvider


class OpenAICompatibleProvider(AIProvider):
    def __init__(self) -> None:
        api_key = os.getenv(API_KEY_ENV or "", "local-api-key")

        client_args = {"api_key": api_key}
        if BASE_URL:
            client_args["base_url"] = BASE_URL

        self.client = OpenAI(**client_args)

    def ask(self, user_message: str) -> str:
        messages = [
            {"role": "system", "content": SYSTEM_INSTRUCTION},
            {"role": "user", "content": user_message},
        ]

        for _ in range(MAX_TOOL_ROUNDS):
            response = self.client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=OPENAI_TOOLS,
                temperature=TEMPERATURE,
            )
            message = response.choices[0].message
            tool_calls = message.tool_calls or []

            if not tool_calls:
                return message.content or "[no text response returned]"

            messages.append(message)

            for tool_call in tool_calls:
                tool_result = self._run_tool_call(
                    tool_call.function.name,
                    tool_call.function.arguments,
                )
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_result,
                    }
                )

        return "stopped because the model exceeded the maximum number of tool rounds."

    def _run_tool_call(self, name: str, raw_arguments: str) -> str:
        tool = TOOL_REGISTRY.get(name)
        if tool is None:
            return f"unknown tool: {name}"

        try:
            arguments = json.loads(raw_arguments or "{}")
        except json.JSONDecodeError as error:
            return f"invalid tool arguments for {name}: {error}"

        if not isinstance(arguments, dict) or not all(
            isinstance(key, str) for key in arguments
        ):
            return f"invalid tool arguments for {name}: expected an object with string keys"

        tool_arguments = cast(dict[str, Any], arguments)

        try:
            return str(tool(**tool_arguments))
        except Exception as error:
            return f"tool error in {name}: {type(error).__name__}: {error}"

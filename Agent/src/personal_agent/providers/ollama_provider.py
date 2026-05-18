import json
from typing import Any, cast

import httpx

from personal_agent.config import (
    BASE_URL,
    MAX_TOOL_ROUNDS,
    MODEL,
    OLLAMA_OPTIONS,
    TEMPERATURE,
)
from personal_agent.prompts import SYSTEM_INSTRUCTION
from personal_agent.tools.registry import TOOL_REGISTRY
from personal_agent.tools.schemas import OPENAI_TOOLS

from personal_agent.providers.base import AIProvider


class OllamaProvider(AIProvider):
    def __init__(self) -> None:
        self.base_url = (BASE_URL or "http://localhost:11434").rstrip("/")
        self.client = httpx.Client(timeout=120.0)

    def ask(self, user_message: str) -> str:
        messages = [
            {"role": "system", "content": SYSTEM_INSTRUCTION},
            {"role": "user", "content": user_message},
        ]

        for _ in range(MAX_TOOL_ROUNDS):
            response = self.client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": MODEL,
                    "messages": messages,
                    "tools": self._ollama_tools(),
                    "stream": False,
                    "options": {
                        "temperature": TEMPERATURE,
                        **OLLAMA_OPTIONS,
                    },
                },
            )
            response.raise_for_status()
            payload = response.json()
            message = payload.get("message", {})
            tool_calls = message.get("tool_calls") or []

            if not tool_calls:
                return message.get("content") or "[no text response returned]"

            messages.append(message)

            for tool_call in tool_calls:
                function_call = tool_call.get("function", {})
                tool_result = self._run_tool_call(
                    function_call.get("name", ""),
                    function_call.get("arguments") or {},
                )
                messages.append(
                    {
                        "role": "tool",
                        "content": tool_result,
                    }
                )

        return "stopped because the model exceeded the maximum number of tool rounds."

    def _ollama_tools(self) -> list[dict]:
        tools = []

        for tool in OPENAI_TOOLS:
            function = tool["function"]
            tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": function["name"],
                        "description": function["description"],
                        "parameters": function["parameters"],
                    },
                }
            )

        return tools

    def _run_tool_call(self, name: str, arguments: dict[str, Any] | str) -> str:
        tool = TOOL_REGISTRY.get(name)
        if tool is None:
            return f"unknown tool: {name}"

        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments or "{}")
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

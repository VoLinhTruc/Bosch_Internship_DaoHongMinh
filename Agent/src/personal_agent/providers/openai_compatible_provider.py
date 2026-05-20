import json
import os
from typing import Any, cast

from openai import OpenAI

from personal_agent.config import (
    API_KEY_ENV,
    BASE_URL,
    MAX_TOOL_ROUNDS,
    MODEL,
    TEMPERATURE,
    USE_TOOLS,
)
from personal_agent.prompts import SYSTEM_INSTRUCTION
from personal_agent.tools.registry import TOOL_REGISTRY
from personal_agent.tools.schemas import OPENAI_TOOLS

from personal_agent.providers.base import AIProvider


class OpenAICompatibleProvider(AIProvider):
    def __init__(self) -> None:
        api_key = os.getenv(API_KEY_ENV or "", "local-api-key")

        client_args = {"api_key": api_key}
        if BASE_URL:
            client_args["base_url"] = BASE_URL

        self.client = OpenAI(**client_args)
        self.model = self._select_model()

    def ask(self, user_message: str) -> str:
        messages = [
            {"role": "system", "content": SYSTEM_INSTRUCTION},
            {"role": "user", "content": user_message},
        ]

        for _ in range(MAX_TOOL_ROUNDS):
            request_args: dict[str, Any] = {
                "model": self.model,
                "messages": messages,
                "temperature": TEMPERATURE,
            }
            if USE_TOOLS:
                request_args["tools"] = OPENAI_TOOLS

            response = self.client.chat.completions.create(**request_args)
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

    def _select_model(self) -> str:
        if MODEL != "auto":
            return MODEL

        try:
            models = self.client.models.list()
        except Exception as error:
            raise RuntimeError(
                "could not list models from the OpenAI-compatible server. "
                f"Tried base URL: {BASE_URL or '[default OpenAI endpoint]'}. "
                "For LM Studio, start the server, load a chat model, and set "
                "LM_STUDIO_BASE_URL when the model is running on another device."
            ) from error

        model_ids = [model.id for model in models.data]
        chat_model_ids = [
            model_id
            for model_id in model_ids
            if "embed" not in model_id.lower() and "nomic" not in model_id.lower()
        ]

        if not chat_model_ids:
            raise RuntimeError(
                "no chat model is loaded on the OpenAI-compatible server. "
                f"Available models: {', '.join(model_ids) or '[none]'}"
            )

        return chat_model_ids[0]

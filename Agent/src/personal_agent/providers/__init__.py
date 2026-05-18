from personal_agent.config import PROVIDER


def create_provider():
    if PROVIDER == "gemini":
        from personal_agent.providers.gemini_provider import GeminiProvider

        return GeminiProvider()

    if PROVIDER == "openai_compatible":
        from personal_agent.providers.openai_compatible_provider import (
            OpenAICompatibleProvider,
        )

        return OpenAICompatibleProvider()

    if PROVIDER == "ollama":
        from personal_agent.providers.ollama_provider import OllamaProvider

        return OllamaProvider()

    raise ValueError(f"unknown provider: {PROVIDER}")

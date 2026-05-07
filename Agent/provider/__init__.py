from config import PROVIDER


def create_provider():
    if PROVIDER == "gemini":
        from provider.gemini_provider import GeminiProvider

        return GeminiProvider()

    if PROVIDER == "openai_compatible":
        from provider.openai_compatible_provider import OpenAICompatibleProvider

        return OpenAICompatibleProvider()

    if PROVIDER == "ollama":
        from provider.ollama_provider import OllamaProvider

        return OllamaProvider()

    raise ValueError(f"unknown provider: {PROVIDER}")

from abc import ABC, abstractmethod


class AIProvider(ABC):
    @abstractmethod
    def ask(self, user_message: str) -> str:
        """Return the provider's final answer for a user message."""

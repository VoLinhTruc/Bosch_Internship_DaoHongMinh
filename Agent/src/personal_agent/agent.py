from personal_agent.providers.base import AIProvider


class Agent:
    def __init__(self, provider: AIProvider) -> None:
        self.provider = provider

    def ask(self, user_message: str) -> str:
        return self.provider.ask(user_message)

from agent import Agent
from config import MODEL, PROVIDER, WORKSPACE
from provider import create_provider


def main() -> None:
    provider = create_provider()
    agent = Agent(provider)

    print(f"provider: {PROVIDER}")
    print(f"model: {MODEL}")
    print(f"workspace: {WORKSPACE}")
    print("type 'exit' to quit.\n")

    while True:
        user_message = input("You> ").strip()

        if user_message.lower() in {"exit", "quit"}:
            break

        if not user_message:
            continue

        try:
            answer = agent.ask(user_message)
        except Exception as error:
            answer = f"error: {type(error).__name__}: {error}"

        print("\nAgent>")
        print(answer)
        print()


if __name__ == "__main__":
    main()

from google import genai

from agent import ask_agent
from config import MODEL, WORKSPACE


def main() -> None:
    client = genai.Client()

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
            answer = ask_agent(client, user_message)
        except Exception as error:
            answer = f"error: {type(error).__name__}: {error}"

        print("\nAgent>")
        print(answer)
        print()


if __name__ == "__main__":
    main()
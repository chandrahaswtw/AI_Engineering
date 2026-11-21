from dotenv import load_dotenv

from ai_engineering.ch01_calling_llms import (
    use_openai,
    use_openai_api,
    use_ollama,
)


# Running load_dotenv() once at the entrypoint (main.py) is enough.
# os.environ is a single global dictionary shared across your entire running Python process. Any module imported or function called after load_dotenv() has access to those environment variables.

load_dotenv()


def main() -> None:
    print(use_ollama())


if __name__ == "__main__":
    main()

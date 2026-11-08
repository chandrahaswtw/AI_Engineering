from dotenv import load_dotenv

from ai_engineering.ch01_exploring_top_models import use_openai

load_dotenv()


def main() -> None:
    print(use_openai())


if __name__ == "__main__":
    main()

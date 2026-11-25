from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

# Ollama exposes an OpenAI-compatible API under /v1.
# The SDK requires an api_key, but Ollama ignores its value.
OLLAMA_BASE_URL = "http://localhost:11434/v1"


def use_ollama() -> str:
    client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
    messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": "Behave like a tamil nadu friend"},
        {
            "role": "user",
            "content": "Hello, GPT! This is my first ever message to you! Hi!",
        },
    ]

    response = client.chat.completions.create(
        model="gemma3:270m",
        messages=messages,
    )

    content = response.choices[0].message.content
    return content or ""

import os
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam


def use_openai() -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set.")

    client = OpenAI()
    messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": "Behave like a tamil nadu friend"},
        {"role": "user", "content": "Hello, GPT! This is my first ever message to you! Hi!"},
    ]

    response = client.chat.completions.create(
        model="gpt-6-luna",
        messages=messages,
    )

    content = response.choices[0].message.content
    return content or ""

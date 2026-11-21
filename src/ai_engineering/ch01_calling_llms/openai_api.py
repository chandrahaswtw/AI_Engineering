import os

import requests

OPENAI_CHAT_COMPLETIONS_URL = "https://api.openai.com/v1/chat/completions"


def use_openai_api() -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gpt-6-luna",
        "messages": [
            {"role": "system", "content": "Behave like a tamil nadu friend"},
            {
                "role": "user",
                "content": "Hello, GPT! This is my first ever message to you! Hi!",
            },
        ],
    }

    response = requests.post(
        OPENAI_CHAT_COMPLETIONS_URL, headers=headers, json=payload, timeout=30
    )
    response.raise_for_status()

    content = response.json()["choices"][0]["message"]["content"]
    return content or ""

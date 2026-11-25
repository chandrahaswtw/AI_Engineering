import os
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

# openAI Python SDK specifically looks for OPENAI_API_KEY env variable.


def use_openai_memory_illusion() -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set.")

    client = OpenAI()
    messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": "Behave like a tamil nadu friend"},
        {
            "role": "user",
            "content": "Hello, GPT! I am chandra",
        },
        {
            "role": "assistant",
            "content": "Hi Chandra, How can I help you maacha",
        },
        {
            "role": "user",
            "content": "Hello, GPT! What is my name",
        },
    ]

    response = client.chat.completions.create(
        model="gpt-6-luna",
        messages=messages,
    )

    content = response.choices[0].message.content
    return content or ""

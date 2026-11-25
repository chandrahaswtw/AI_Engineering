import tiktoken


def use_tiktoken() -> None:
    text = "Hello, world! Tiktoken is fast."
    encoding = tiktoken.encoding_for_model("gpt-4o")

    # Encode: text -> token IDs
    tokens = encoding.encode(text)

    # Decode: token IDs -> text
    decoded = encoding.decode(tokens)

    print(f"Original: {text}\nTokens: {tokens}\nDecoded: {decoded}")

# Chapter 1: Calling LLMs

This package sends the same chat request to a model in three different ways. The request has a system prompt ("Behave like a tamil nadu friend") and a user greeting. Comparing the three shows what an SDK does for you and how one client can talk to different providers.

| File | Function | Provider | How the call is made |
|------|----------|----------|----------------------|
| [`openai_client.py`](openai_client.py) | `use_openai()` | OpenAI | `openai` SDK |
| [`openai_api.py`](openai_api.py) | `use_openai_api()` | OpenAI | Raw HTTP with `requests` |
| [`ollama_api.py`](ollama_api.py) | `use_ollama()` | Ollama (local) | `openai` SDK, pointed at Ollama |

All three functions return the model's reply as a `str`. They are exported from [`__init__.py`](__init__.py).

## The files

### `openai_client.py`: OpenAI via the SDK

Uses `OpenAI()` and `client.chat.completions.create(...)`. The SDK reads `OPENAI_API_KEY` from the environment on its own. The function also checks that the variable is set, so a missing key gives a clear error.

### `openai_api.py`: OpenAI via a raw HTTP call

Does the same thing without the SDK. It sends a `POST` to `https://api.openai.com/v1/chat/completions` with `requests`:

- The API key goes in an `Authorization: Bearer <key>` header.
- The model and messages go in a JSON body.
- `response.raise_for_status()` raises an `HTTPError` on 4xx/5xx responses (bad key, rate limit, wrong model name). Without it, the error body would be parsed as if it were a successful reply.
- The reply is at `response.json()["choices"][0]["message"]["content"]`.

This is what the SDK does under the hood.

### `ollama_api.py`: Ollama via the OpenAI SDK

Ollama serves an OpenAI-compatible API at `http://localhost:11434/v1`. The code is the same as `openai_client.py` except for the client:

```python
OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
```

- `base_url` sends the SDK's requests to the local Ollama server instead of OpenAI.
- The SDK requires an `api_key`, but Ollama ignores the value, so `"ollama"` is a placeholder. This function doesn't use `OPENAI_API_KEY`.
- The model is `gemma3:270m`. It has to be pulled first (`ollama pull gemma3:270m`), and `ollama list` shows what is installed.

## How Ollama uses the OpenAI SDK (and using it with non-OpenAI models)

### The idea

The OpenAI SDK is an HTTP client for one API shape: `POST {base_url}/chat/completions` with a JSON body of `model` and `messages`, returning `choices[0].message.content`. Nothing in the SDK checks that the server is actually OpenAI. It sends that request to whatever `base_url` it is given.

So any server that implements the same endpoints and JSON format works with the SDK unchanged. Ollama does this by serving an OpenAI-compatible API under `/v1`.

```
OpenAI SDK  --POST http://localhost:11434/v1/chat/completions-->  Ollama  -->  gemma3:270m
```

### What changes between OpenAI and Ollama

Only the client construction:

```python
# OpenAI
client = OpenAI()  # base_url defaults to https://api.openai.com/v1, key from OPENAI_API_KEY

# Ollama
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
```

Everything after that is identical: `client.chat.completions.create(model=..., messages=...)`, the message format, and reading `response.choices[0].message.content`. Only the `model` value changes (`gemma3:270m` is an Ollama model name).

- `base_url`: where requests go.
- `api_key`: the SDK refuses to build a client without one. Ollama has no auth and ignores it, so any string works.
- `model`: must be a model the target server knows about.

This is the same call as the raw `requests` version in `openai_api.py`, just with a different URL.

### Other providers that work the same way

Many providers and tools expose an OpenAI-compatible endpoint, so the same SDK works by changing `base_url`, `api_key` and `model`:

| Target | Typical `base_url` |
|--------|--------------------|
| Ollama (local) | `http://localhost:11434/v1` |
| LM Studio (local) | `http://localhost:1234/v1` |
| vLLM (self-hosted) | `http://localhost:8000/v1` |
| OpenRouter, Together, Groq, etc. | provider's documented `/v1` URL (check their docs, since they change) |

Pass the provider's own API key and model name. Hosted providers need a real key.

### Why this matters

- **Switching providers is cheap.** Code written against the SDK can move between OpenAI, a local model and other providers by changing config, not logic.
- **Local development is free.** You can build and test against Ollama, then point at a hosted model later.
- **No lock-in to the SDK's models.** The SDK is just the transport. The model is whatever is behind the URL.

### Caveats

- **Compatibility varies.** `chat/completions` basics (messages, `model`, `temperature`, `max_tokens`, streaming) are usually supported. Newer or OpenAI-specific features may be missing or behave differently, such as the Responses API, some tool-calling and structured-output options, embeddings, images and audio. Check the provider's compatibility docs.
- **Model names are provider-specific.** `gpt-...` names only exist at OpenAI. Ollama uses names from `ollama list`.
- **Response quality and behavior differ by model.** `gemma3:270m` is tiny, so its replies are far weaker than a hosted model's.
- **Type hints still say "OpenAI".** Imports like `ChatCompletionMessageParam` only describe the request shape. They don't tie you to OpenAI's servers.

## Running

[`main.py`](../main.py) calls `load_dotenv()` once at startup, so variables from a `.env` file are available to every module. `main()` currently calls `use_ollama()`. To try another one, change the function it calls.

```bash
uv run ai-engineering
```

Requirements:

- **OpenAI functions:** `OPENAI_API_KEY` set in the environment or in `.env`.
- **Ollama:** the Ollama server running locally and the model pulled.

## Notes

- `use_openai()` and `use_openai_api()` use the model name `gpt-6-luna`. Change it if your key can't use that model.
- `use_openai_api()` handles HTTP errors only through `raise_for_status()`. Timeouts, connection failures and unexpected response shapes are not handled specially.

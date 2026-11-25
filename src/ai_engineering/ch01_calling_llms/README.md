# Chapter 1: Calling LLMs

This package sends the same chat request to a model in three different ways. The request has a system prompt ("Behave like a tamil nadu friend") and a user greeting. Comparing the three shows what an SDK does for you and how one client can talk to different providers.

| File | Function | Provider | How the call is made |
|------|----------|----------|----------------------|
| [`s01_openai_client.py`](s01_openai_client.py) | `use_openai()` | OpenAI | `openai` SDK |
| [`s02_openai_api.py`](s02_openai_api.py) | `use_openai_api()` | OpenAI | Raw HTTP with `requests` |
| [`s03_ollama_api.py`](s03_ollama_api.py) | `use_ollama()` | Ollama (local) | `openai` SDK, pointed at Ollama |
| [`s04_tiktoken_example.py`](s04_tiktoken_example.py) | `use_tiktoken()` | Local / OpenAI Tokenizer | `tiktoken` BPE tokenization & token counting |
| [`s05_illusion_of_memory.py`](s05_illusion_of_memory.py) | `use_openai_memory_illusion()` | OpenAI | Multi-turn chat history via `messages` |

All functions are exported from [`__init__.py`](__init__.py).

## The files

### `s01_openai_client.py`: OpenAI via the SDK

Uses `OpenAI()` and `client.chat.completions.create(...)`. The SDK reads `OPENAI_API_KEY` from the environment on its own. The function also checks that the variable is set, so a missing key gives a clear error.

### `s02_openai_api.py`: OpenAI via a raw HTTP call

Does the same thing without the SDK. It sends a `POST` to `https://api.openai.com/v1/chat/completions` with `requests`:

- The API key goes in an `Authorization: Bearer <key>` header.
- The model and messages go in a JSON body.
- `response.raise_for_status()` raises an `HTTPError` on 4xx/5xx responses (bad key, rate limit, wrong model name). Without it, the error body would be parsed as if it were a successful reply.
- The reply is at `response.json()["choices"][0]["message"]["content"]`.

This is what the SDK does under the hood.

### `s03_ollama_api.py`: Ollama via the OpenAI SDK

Ollama serves an OpenAI-compatible API at `http://localhost:11434/v1`. The code is the same as `s01_openai_client.py` except for the client:

```python
OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
```

- `base_url` sends the SDK's requests to the local Ollama server instead of OpenAI.
- The SDK requires an `api_key`, but Ollama ignores the value, so `"ollama"` is a placeholder. This function doesn't use `OPENAI_API_KEY`.
- The model is `gemma3:270m`. It has to be pulled first (`ollama pull gemma3:270m`), and `ollama list` shows what is installed.

### `s04_tiktoken_example.py`: Tokenization with `tiktoken`

Demonstrates how text is encoded into token IDs and decoded back into text using OpenAI's `tiktoken` library.

```python
encoding = tiktoken.encoding_for_model("gpt-4o")
tokens = encoding.encode("Hello, world!")
decoded = encoding.decode(tokens)
```

### `s05_illusion_of_memory.py`: The Illusion of Memory

Demonstrates how multi-turn conversational memory works in LLMs by passing past `user` and `assistant` turns in the `messages` array.

```python
messages = [
    {"role": "system", "content": "Behave like a tamil nadu friend"},
    {"role": "user", "content": "Hello, GPT! I am chandra"},
    {"role": "assistant", "content": "Hi Chandra, How can I help you maacha"},
    {"role": "user", "content": "Hello, GPT! What is my name"},
]
```

## The Illusion of Memory: Why LLMs are Stateless

### 1. LLMs have zero server-side memory
Language models and API servers are **completely stateless**. They do not store previous messages, user identities, or chat histories across API calls. Every API request is treated as if it were the first time the model has ever run.

### 2. Memory is maintained entirely by the client
When chat applications (like ChatGPT) appear to remember previous turns, the client application is simply saving the conversation log and **resending the entire conversation history** in the `messages` list with every new user query.

- **With history sent**: The model sees the prior `"I am chandra"` text within its prompt context and answers correctly.
- **Without history sent**: The model only receives `"What is my name"` with no context, and cannot know who you are.

## What is the Context Window?

### Definition
The **Context Window** is the maximum total number of tokens (input prompt + generated output so far) that a model can process and hold in its attention mechanism at any single moment when generating the next token.

> **Note:** Output tokens are also part of the context window. Because LLMs generate text autoregressively (one token at a time), each newly generated token is appended to the context when predicting the next token.

$$\text{Input Tokens} + \text{Output Tokens} \le \text{Context Window Limit}$$

### Does the Context Window contain the old chat?
**Yes, but only if you explicitly send it in your API call.**

Because LLMs are stateless, previous conversation turns do not persist on the server. When you pass past messages into the `messages` array, they take up space inside the current request's context window budget:

```
┌────────────────────────────────────────────────────────┐
│                   TOTAL CONTEXT WINDOW                  │
├────────────────────────────────────────────────────────┤
│ 1. System Prompt ("Behave like a tamil nadu friend")   │
│ 2. Past User Message 1 ("Hello, I am chandra")         │ ← Old Chat (History)
│ 3. Past Assistant Reply 1 ("Hi Chandra, how can I...") │ ← Old Chat (History)
│ 4. Current User Message ("What is my name?")           │ ← New Message
│ 5. Model's Generated Output (tokens generated so far)  │ ← Output
└────────────────────────────────────────────────────────┘
```

### Key Implications in Practice
1. **Chat history consumes token budget**: Every past question and answer resubmitted in `messages` eats into your available context window and increases API cost.
2. **Context Window Overflow**: In long conversations, accumulated history will eventually exceed the model's limit (e.g., 128k tokens for `gpt-4o`).
3. **Techniques for managing long chats**:
   - **Sliding Window / Truncation**: Dropping the oldest turns when approaching the token limit.
   - **Conversation Summarization**: Using an LLM to periodically summarize older turns and keeping only the running summary.
   - **RAG / Vector Retrieval**: Storing past conversation turns in a database and retrieving only turns relevant to the current prompt.

## How LLM API Costs Work

API pricing is based on **token usage** split into two billing categories:

$$\text{Total Cost} = (\text{Input Tokens} \times \text{Input Price}) + (\text{Output Tokens} \times \text{Output Price})$$

| Component | What it includes | Pricing |
|---|---|---|
| **Input (Prompt) Tokens** | System prompt, resubmitted chat history, current user message, RAG context, tool schemas. | **Cheaper** (processed in parallel on GPUs) |
| **Output (Completion) Tokens** | Generated response text, generated tool call arguments, internal reasoning tokens. | **More expensive** (typically 3x–4x higher because generation is sequential/autoregressive) |

### Do Hidden Reasoning Tokens Cost Money?
**Yes.** For reasoning models (such as OpenAI `o1`, `o1-mini`, `o3`), internal chain-of-thought tokens generated during reasoning are **billed as output tokens**, even if they are hidden and not shown in the final visible response.

$$\text{Billed Output Tokens} = \text{Visible Response Tokens} + \text{Hidden Reasoning Tokens}$$

Providers charge for these tokens because generating internal reasoning steps consumes the same GPU compute time, memory, and context window space as generating regular text.

## What is `tiktoken` and what does it do?

**`tiktoken`** is OpenAI's fast, open-source **BPE (Byte Pair Encoding) tokenizer** library written in Rust with Python bindings.

### Core Purpose

Large Language Models (LLMs) do not process text as strings or characters. Instead, they process sequences of numbers called **token IDs**, where each token represents a word, subword, punctuation mark, or whitespace.

`tiktoken` performs two-way conversion:

1. **Encoding (`text -> token IDs`)**: Breaks down text into subwords and maps them to integer IDs.
   ```python
   encoding.encode("Hello, world! Tiktoken is fast.")
   # -> [13225, 11, 2375, 0, 353, 8251, 2488, 382, 5661, 13]
   ```
2. **Decoding (`token IDs -> text`)**: Reconstructs the original string from token IDs.
   ```python
   encoding.decode([13225, 11, 2375, 0, ...])
   # -> "Hello, world! Tiktoken is fast."
   ```

### Why use `tiktoken` in AI Engineering?

- **Cost Estimation**: LLM APIs charge per input and output token. `tiktoken` lets you calculate token usage and costs before sending a request.
- **Context Window Management**: Models enforce strict token limits (e.g., 128k tokens for `gpt-4o`). Token counting prevents prompts or chat histories from being unexpectedly cut off.
- **RAG & Document Chunking**: Splitting documents by token count (rather than raw character count) ensures chunks fit model context and embedding boundaries cleanly.
- **Speed**: Built in Rust, `tiktoken` is significantly faster than standard pure-Python tokenizers when processing large volumes of text.

### Common Encodings by Model

| Encoding | Primary Models | Vocabulary Size |
|---|---|---|
| `o200k_base` | `gpt-4o`, `gpt-4o-mini`, `o1` | ~200,000 tokens |
| `cl100k_base` | `gpt-4`, `gpt-3.5-turbo`, `text-embedding-3-*` | ~100,000 tokens |
| `p50k_base` | Legacy GPT-3 models (e.g., `text-davinci-003`) | ~50,000 tokens |

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

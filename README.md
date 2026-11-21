# AI Engineering

Personal notes and code while learning AI engineering. This page is a beginner-friendly intro to the kinds of language models (LLMs) you'll run into.

## What is an LLM?

A Large Language Model (LLM) is a program trained on huge amounts of text to predict what text should come next. That one skill lets it answer questions, write code, summarise documents and hold a conversation.

A model is mostly a big file of numbers called **weights** (also called parameters). Training adjusts the weights. Running the model ("inference") uses them to produce text.

## Closed-source vs open-source LLMs

### Closed-source (proprietary) models

The weights are kept private by the company. You can only use the model through their API or app, and you pay per use.

- **Examples:** OpenAI's GPT models, Anthropic's Claude, Google's Gemini.
- **Pros:** Usually the most capable models, no hardware to manage, easy to start with.
- **Cons:** Costs money, your data goes to a third party, you can't change the model, and the provider can change or retire it.

### Open models

The weights are published, so you can download and run them yourself, on your laptop or your own servers.

- **Examples:** Meta's Llama, Mistral models, Google's Gemma, Qwen, DeepSeek.
- **Pros:** Free to run (you pay for hardware), data stays with you, can be customised (fine-tuned), works offline.
- **Cons:** You need suitable hardware, bigger models are expensive to run, and the very best models are often still closed.

**Open source vs open weights.** Most "open source" LLMs are really **open weights**. You get the trained model but usually not the training data or full training code. Licences also differ: some allow any use, others limit commercial use. Check the licence before building a product on one.

### Quick comparison

| | Closed | Open |
|---|---|---|
| Access | API / app | Download the weights |
| Cost | Pay per use | Hardware and electricity |
| Privacy | Data sent to provider | Can stay fully local |
| Customisation | Limited | Full control |
| Setup effort | Low | Higher |

## How you use them in this repo

Both kinds can be called with the same client code. See [`ch01_calling_llms`](src/ai_engineering/ch01_calling_llms/README.md):

- OpenAI (closed) is called through its API.
- Ollama runs open models locally, such as Gemma. It exposes an OpenAI-compatible endpoint, so the OpenAI SDK can talk to it.

## Model size

Models are often named with a size, like `gemma3:270m` or `llama-70b`. The number is the count of parameters (`m` = million, `b` = billion).

- More parameters usually means smarter but slower and more memory-hungry.
- Small models can run on a laptop. The biggest need data-centre GPUs.

## Distillation

**Distillation** is a way to make a small model that imitates a big one.

1. A large, capable **teacher** model produces answers (and sometimes its confidence across possible answers).
2. A smaller **student** model is trained to reproduce those outputs.
3. The student ends up much cheaper and faster, and keeps a good part of the teacher's ability.

An analogy: a student learns from an expert's worked solutions instead of working it all out from raw textbooks.

- **Why it's used:** Smaller models cost less, respond faster and can run on devices like phones and laptops.
- **Trade-off:** The student is usually a bit worse than the teacher, especially on hard tasks.
- **Licensing:** Providers' terms may restrict using their model's outputs to train a competing model, so check them.

## Other terms you'll see

- **Fine-tuning:** Training an existing model a little more on your own data to specialise it, for example for a certain tone or domain.
- **Quantization:** Storing the weights with fewer bits, such as 4-bit instead of 16-bit. The model gets smaller and faster with a small drop in quality. Many models you download with Ollama are quantized.
- **Inference:** Running a trained model to get outputs (as opposed to training it).
- **Context window:** How much text the model can consider at once, covering your prompt and its reply.
- **Tokens:** The chunks of text a model reads and writes, roughly a word or part of a word. APIs usually bill by token.
- **Hallucination:** When a model states something false with confidence. Always verify important facts.

## Which should I use?

- Learning, prototyping, or needing top quality quickly: a closed API is the easiest start.
- Privacy, offline use, cost control or experimenting: try an open model locally with Ollama.
- It's common to prototype on one and switch to the other later, which is why the shared API format matters.

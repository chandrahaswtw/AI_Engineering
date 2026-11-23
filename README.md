# AI Engineering

Personal notes and code while learning AI engineering. This page is a beginner-friendly intro to the kinds of language models (LLMs) you'll run into.

## What is an LLM?

A Large Language Model (LLM) is a program trained on huge amounts of text to predict what text should come next. That one skill lets it answer questions, write code, summarise documents and hold a conversation.

A model is mostly a big file of numbers called **weights** (also called parameters). Training adjusts the weights. Running the model ("inference") uses them to produce text.

## GPT: Generative pre-trained transformer.

### The problem it solved
Earlier models for text (RNNs, LSTMs) read words one at a time, in order, and carried a running memory forward. That was slow to train, because it couldn't be parallelised well, and the memory faded over long text. Words far apart struggled to influence each other.

### The core idea: attention
Instead of reading word by word, a transformer looks at all the words at once. For each word, it works out which other words matter most for its meaning. This is called self-attention.

Example: in "The animal didn't cross the street because it was too tired", attention helps the model link "it" to "animal" and not "street".

## What are parameters?

A parameter is a number that an AI model learns during training. Inside the neural network, parameters act like tiny adjustable knobs that shape the model's final answer.

During training, the model reads large amounts of data, makes predictions, checks how wrong they are, and adjusts its parameters to reduce the mistakes. This loop repeats over trillions of tokens of text. The model ends up with a massive collection of numerical settings. These settings are its parameters.

## What are tokens?

Tokens are the small units of text that an LLM processes and generates. A token can be:

- An entire word.
- Part of a word.
- A punctuation mark.
- A number or other character sequence.

Tokens are not necessarily the same as words. APIs usually bill by token.

The **context window** is the maximum number of tokens a model can consider at once, covering both your prompt and its reply. It is a hard limit, which matters for RAG later.

### Try it: OpenAI Tokenizer

[platform.openai.com/tokenizer](https://platform.openai.com/tokenizer) is a free tool from OpenAI. You paste in text and it shows how that text is split into tokens, with each token highlighted and the total token count displayed.

Different model families use different tokenizers, so counts from this tool are exact only for OpenAI models. For other models such as Llama or Gemma, treat them as a rough estimate.



## What is inference?

**Inference** means using a trained model to generate a response. Training changes the parameters. Inference only uses them.

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

## Frontier models

The **frontier models** are the most capable models available at a given time, such as the latest flagship models from OpenAI, Anthropic and Google. They cost the most to train and run, and today's frontier is usually mid-tier within a year or two.

Most frontier models are closed, so you can only use them through the provider's API. Some open-weight models (for example the larger Llama, DeepSeek and Qwen models) score close to them on many benchmarks, and you can download and run those yourself. The gap varies by task and over time: the best closed models often still lead on hard reasoning and coding, and the biggest open models need serious hardware, so being close in quality doesn't mean being easy to run on a laptop.

## Base, chat and reasoning models

Models are trained in stages, and the same family often ships several versions:

- **Base (pretrained):** Trained only to predict the next token. It continues text but doesn't reliably follow instructions. Mainly a starting point for fine-tuning. Often named `base` or `pt`.
- **Instruction-tuned / chat:** A base model trained further to follow instructions and hold a conversation. This is what you call with `chat/completions` and what this repo uses. Often named `instruct`, `it` or `chat`.
- **Reasoning:** A chat model trained to think step by step before answering. Better at maths, code and logic, but slower and costlier, so it is overkill for simple tasks.

A reasoning model is mostly a different training recipe, not a different architecture. Many newer models combine chat and reasoning, so check each model's description.

## Distillation

**Distillation** is a way to make a small model that imitates a big one.

1. A large, capable **teacher** model produces answers (and sometimes its confidence across possible answers).
2. A smaller **student** model is trained to reproduce those outputs.
3. The student ends up much cheaper and faster, and keeps a good part of the teacher's ability.

An analogy: a student learns from an expert's worked solutions instead of working it all out from raw textbooks.

- **Why it's used:** Smaller models cost less, respond faster and can run on devices like phones and laptops.
- **Trade-off:** The student is usually a bit worse than the teacher, especially on hard tasks.
- **Licensing:** Providers' terms may restrict using their model's outputs to train a competing model, so check them.

## What does a model know without the internet?

A local model can answer questions without an internet connection because it learned patterns, relationships and information during training. It does not store facts like a database or a set of organised records. Knowledge is spread across the parameters as statistical patterns.

So what if you ask something the model has never encountered? It might:

- Tell you it doesn't have that information.
- Generate a plausible but incorrect answer. This is called a **hallucination**.
- Answer using information already present in your prompt.

This is where RAG comes in.

## RAG (Retrieval-Augmented Generation)

**Definition:** RAG is an architecture that retrieves relevant information from external knowledge sources and provides it as context to an LLM, so it can generate more relevant and informed answers.

RAG does not necessarily require the internet. You can retrieve information from local documents or databases too.

### Model vs application

No LLM, open or closed, has RAG built in. RAG, web search and external tools come from the **application built around the model**. Closed-source products like ChatGPT bundle these features for you. With a local model such as Llama running in Ollama, you build that layer yourself.

### 1. Knowledge sources

RAG can retrieve information from:

- Documents: PDF, Word, TXT, Markdown.
- Databases: MySQL, PostgreSQL, MongoDB.
- Websites: internet URLs and technical documentation.
- APIs and cloud storage.

Vector databases such as ChromaDB and Pinecone are not original sources. They are where the embeddings of those sources are stored (see step 4 below).

### 2. How RAG works

1. **Data ingestion:** Collect information from documents, databases or websites.
2. **Chunking:** Split large documents into smaller sections. This is needed because of the model's limited context window.
3. **Embedding:** Convert each chunk into a numerical vector with an embedding model.
4. **Storage:** Store the embeddings, along with the original chunk text, in a vector database (commonly used).
5. **Retrieval:** Embed the user's question with the same embedding model, then find the stored chunks whose vectors are most similar to it.
6. **Generation:** Pass the retrieved chunks to the LLM as context to generate an answer.

The LLM never sees the vectors. It only sees the retrieved text. The vectors are just how you search.

### 3. RAG approaches

- **Pre-indexed RAG:** Fetch and index information beforehand. Retrieve relevant content from the stored knowledge base when a question arrives.
- **Dynamic retrieval:** Fetch information from URLs, websites or APIs when a question arrives, then pass it straight to the LLM.

### 4. RAG vs web search

| RAG | Web search |
|---|---|
| Architecture for retrieving relevant knowledge and augmenting LLM prompts. | Capability to find information on the internet. |
| Can use documents, databases, websites, APIs, etc. | Primarily searches online sources. |
| Can work without internet. | Usually requires internet. |
| Commonly uses vector databases, but doesn't require them. | Doesn't require vector databases. |
| Often retrieves from a predefined knowledge base. | Can discover new and current online information. |
| Can work with private company documentation. | Usually searches publicly accessible information. |

**Can they work together?** Yes. Web search can act as a retrieval source in a RAG workflow. For example, an AI assistant could:

- Use RAG to retrieve internal company documentation.
- Use web search to find the latest public documentation.
- Pass both sets of information to an LLM to generate an answer.

### 5. Example technology stack

| Component | Technology |
|---|---|
| LLM | Llama model, run via Ollama |
| RAG framework | LangChain / LlamaIndex |
| Embeddings | An embedding model, for example `nomic-embed-text` |
| Vector database | ChromaDB |
| Web retrieval | Search API / web scraper |

### 6. Important points to remember

- RAG does not inherently require a vector database.
- RAG does not inherently require internet access.
- Web search and RAG can work together.
- RAG provides additional context. It does not retrain or modify the LLM's parameters, so you can update the knowledge without retraining.
- RAG reduces hallucination but does not remove it. Poor retrieval leads to poor answers, and the model can still ignore or misread the context.

### Three concepts to remember

1. **LLM parameters:** What the model learned during training.
2. **Inference:** Using what the model learned to generate responses.
3. **RAG:** Giving the model access to additional external information when answering.

**Key takeaway:** RAG gives an LLM access to external knowledge at inference time, allowing it to answer questions using information beyond what it learned during training. Web search finds information on the internet, whereas RAG is an architecture for retrieving relevant information and adding it to the LLM's input.

## Other terms you'll see

- **Fine-tuning:** Training an existing model a little more on your own data to specialise it, for example for a certain tone or domain.
- **Quantization:** Storing the weights with fewer bits, such as 4-bit instead of 16-bit. The model gets smaller and faster with a small drop in quality. Many models you download with Ollama are quantized.
- **Hallucination:** When a model states something false with confidence. Always verify important facts.

## Which should I use?

- Learning, prototyping, or needing top quality quickly: a closed API is the easiest start.
- Privacy, offline use, cost control or experimenting: try an open model locally with Ollama.
- It's common to prototype on one and switch to the other later, which is why the shared API format matters.

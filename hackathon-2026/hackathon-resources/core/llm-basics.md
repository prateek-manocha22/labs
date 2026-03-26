# 🧠 LLM Basics & Prompt Engineering

## 1. What are LLMs?
Large Language Models (LLMs) are deep learning models trained on massive datasets to understand and generate human-like text.
- **Why it matters**: They are the reasoning engine of your hackathon project.
- **Resources**:
  - [Generative AI for Beginners (Microsoft)](https://github.com/microsoft/generative-ai-for-beginners)
  - [LLM Fundamentals (DeepLearning.AI)](https://www.deeplearning.ai/short-courses/)
  - [Transformer Architecture Explained (Google Blog)](https://blog.google/technology/ai/transformer-model/)

## 2. Prompt Engineering
The art of crafting inputs to get the best outputs from an AI.

### Core Techniques
| Technique | When to Use |
|---|---|
| **System Prompt** | Set role, tone, and output rules |
| **Few-Shot** | Show examples of input → output |
| **Chain-of-Thought** | Complex reasoning tasks — add "think step by step" |
| **JSON Mode** | Force structured output (use `response_format={"type":"json_object"}`) |
| **ReAct** | Agent tasks where the model needs to reason + act in a loop |

### Anti-Patterns to Avoid
- Vague prompts like "summarize this" — always specify format and length.
- Expecting factual accuracy without RAG — LLMs hallucinate. Ground them.
- Asking the model to do too many things at once — break into steps.

- **Resources**:
  - [Prompt Engineering Guide (PromptingGuide.ai)](https://www.promptingguide.ai/)
  - [OpenAI Prompt Engineering Best Practices](https://platform.openai.com/docs/guides/prompt-engineering)
  - [Learn Prompting (Open Source Course)](https://learnprompting.org/)

## 3. Tokenization & Embeddings
How AI "sees" text (every word/subword = 1 token, and tokens cost money).
- **Rule of thumb**: 1 token ≈ 4 characters in English.
- **Resources**:
  - [OpenAI Tokenizer Tool](https://platform.openai.com/tokenizer)
  - [What are Vector Embeddings? (Pinecone Guide)](https://www.pinecone.io/learn/vector-embeddings/)

## 4. Key Models Quick Reference
| Model | Provider | Best For |
|---|---|---|
| GPT-4o | OpenAI | General reasoning, JSON |
| Claude 3.5 Sonnet | Anthropic | Long docs, code |
| Gemini 1.5 Flash | Google | Fast, cost-effective |
| Llama 3 | Meta | Local/open-source |
| Mistral | Mistral AI | Lightweight deployment |

> See also: [Fine-Tuning Guide](./fine-tuning.md)

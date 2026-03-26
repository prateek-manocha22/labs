# 🛠️ AI Hackathon 2026: Starter Kits

Building from scratch is hard. Use these templates to jumpstart your prototype.

---

## 🟢 Beginner (Zero-Framework)
- [**llm-basic**](./llm-basic/) — Simplest way to chat with an LLM using raw Python `requests`. **Start here if you're new!**

## 🟡 Intermediate (Track-Specific)
- [**cv-traffic**](./cv-traffic/) — Real-time vehicle detection logic using YOLOv8.
- [**data-processing**](./data-processing/) — Cleaning and normalizing datasets for RL or Fine-Tuning.

## 🔴 Advanced (Agentic & RAG)
- [**mcp-agent**](./mcp-agent/) — Building an MCP-powered agent with tool-use capabilities. [**Advanced/Optional**]
- [**rag-pipeline**](./rag-pipeline/) — Dense retrieval pipeline using ChromaDB and Sentence-Transformers. [**Advanced/Optional**]

---

## 🛠️ Global Setup
All kits require a `.env` file for API keys.
1. Copy `.env.example` to `.env`.
2. Add your keys (OpenAI, Anthropic, etc.).
3. Run `pip install -r requirements.txt`.

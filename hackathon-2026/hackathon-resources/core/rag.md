# 📚 RAG (Retrieval Augmented Generation)

## 1. What is RAG?
RAG allows an LLM to access data it wasn't trained on (your docs, a database, live data).
- **Why it matters**: The #1 way to reduce hallucinations and ground AI in real data.

### RAG Pipeline
```
Document → Chunk → Embed → Store in VectorDB
Query → Embed → Retrieve Top-K chunks → Inject into Prompt → LLM answers
```

- **Resources**:
  - [RAG Explained (AWS)](https://aws.amazon.com/what-is/retrieval-augmented-generation/)
  - [LangChain RAG Tutorial](https://python.langchain.com/docs/tutorials/rag/)

## 2. Chunking Strategies
How you split documents matters a lot:

| Strategy | Description | Best For |
|---|---|---|
| **Fixed-size** | Split every N characters | Simple docs |
| **Recursive text** | Split on `\n`, then space — LangChain default | General purpose |
| **Semantic chunking** | Split when topic changes (embedding similarity) | Long, varied docs |
| **By section** | Split on headers (`##`) | Markdown/HTML docs |

> **Hackathon tip**: Use `RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)` — it works well for most documents.

## 3. Vector Databases
| DB | When to Use |
|---|---|
| **ChromaDB** | Local, quick setup — great for hackathons |
| **FAISS** | Fast in-memory, Meta-backed |
| **Pinecone** | Production, serverless |

- **Resources**:
  - [ChromaDB Quickstart](https://docs.trychroma.com/getting-started)
  - [FAISS Documentation (Meta)](https://github.com/facebookresearch/faiss)

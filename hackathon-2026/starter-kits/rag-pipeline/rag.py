"""
RAG Pipeline Starter Kit — ChromaDB + Sentence Transformers
Run: pip install -r requirements.txt
"""
import os
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# ── Config ─────────────────────────────────────────────────────────────────────
COLLECTION_NAME = "hackathon-docs"
MODEL_NAME      = "all-MiniLM-L6-v2"      # Fast, good quality, runs CPU

# ── Sample knowledge base (replace with your real documents) ──────────────────
SAMPLE_DOCUMENTS = [
    "YOLO is a real-time object detection model used for vehicle detection in traffic systems.",
    "RAG (Retrieval Augmented Generation) grounds LLM responses in verified external documents.",
    "MCP (Model Context Protocol) is a standard by Anthropic for connecting LLMs to external tools.",
    "TOON is a token-efficient alternative to JSON for communicating structured data to LLMs.",
    "Hallucination in LLMs refers to generating plausible but factually incorrect statements.",
]


def build_index(documents: list[str]) -> chromadb.Collection:
    """Embed and store documents in ChromaDB."""
    ef = SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)
    client = chromadb.Client()
    col = client.get_or_create_collection(COLLECTION_NAME, embedding_function=ef)
    col.add(
        documents=documents,
        ids=[f"doc-{i}" for i in range(len(documents))],
    )
    return col


def retrieve(col: chromadb.Collection, query: str, top_k: int = 2) -> list[str]:
    """Retrieve the top-K most relevant document chunks."""
    results = col.query(query_texts=[query], n_results=top_k)
    return results["documents"][0]


def answer(col: chromadb.Collection, question: str) -> str:
    """
    Retrieve context then call an LLM with it.
    Replace the mock below with a real LLM call.
    """
    context_chunks = retrieve(col, question)
    context = "\n".join(context_chunks)

    # ── Swap this with your real LLM provider ─────────────────────────────────
    # from openai import OpenAI
    # client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    # prompt = f"Answer using ONLY the context below.\nContext:\n{context}\n\nQuestion: {question}"
    # return client.chat.completions.create(model="gpt-4o", messages=[{"role":"user","content":prompt}])
    #         .choices[0].message.content
    # ─────────────────────────────────────────────────────────────────────────

    return f"[MOCK ANSWER based on context]\n{context}"


if __name__ == "__main__":
    print("Building index...")
    collection = build_index(SAMPLE_DOCUMENTS)

    questions = [
        "What is YOLO used for?",
        "How does RAG reduce hallucinations?",
    ]
    for q in questions:
        print(f"\n❓ {q}")
        print(f"💡 {answer(collection, q)}")

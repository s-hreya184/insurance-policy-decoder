"""
rag.py — RAG pipeline using Groq embeddings + pure numpy vector store
No ChromaDB — avoids Python 3.14 / protobuf compatibility issues on Streamlit Cloud
"""

import hashlib
import math
import re

import streamlit as st
from groq import Groq

# ── Config ─────────────────────────────────────────────────────────────────────

EMBED_MODEL   = "nomic-embed-text-v1_5"
CHUNK_SIZE    = 800
CHUNK_OVERLAP = 120
TOP_K         = 6


# ── Groq client ────────────────────────────────────────────────────────────────

def _client() -> Groq:
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        raise RuntimeError("GROQ_API_KEY not found in Streamlit secrets.")
    return Groq(api_key=api_key)


# ── Pure-python cosine similarity vector store ────────────────────────────────

def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot   = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def _get_store() -> dict:
    """
    Session-scoped in-memory vector store.
    Structure: { doc_id: { "chunks": [...], "embeddings": [[...], ...] } }
    """
    if "vector_store" not in st.session_state:
        st.session_state["vector_store"] = {}
    return st.session_state["vector_store"]


# ── Groq embeddings ────────────────────────────────────────────────────────────

def _embed(texts: list[str]) -> list[list[float]]:
    client = _client()
    embeddings = []
    for text in texts:
        try:
            response = client.embeddings.create(
                model=EMBED_MODEL,
                input=text,
            )
            embeddings.append(response.data[0].embedding)
        except Exception as e:
            raise RuntimeError(f"Groq embedding failed: {e}")
    return embeddings


# ── Semantic chunking ──────────────────────────────────────────────────────────

def _semantic_chunk(text: str) -> list[str]:
    text = re.sub(r"\r\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    paragraphs = [p.strip() for p in re.split(r"\n\n+", text) if p.strip()]
    chunks: list[str] = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) + 2 <= CHUNK_SIZE:
            current = (current + "\n\n" + para).strip()
        else:
            if current:
                chunks.append(current)
            if len(para) > CHUNK_SIZE:
                sentences = re.split(r"(?<=[.!?])\s+", para)
                sub = ""
                for sent in sentences:
                    if len(sub) + len(sent) + 1 <= CHUNK_SIZE:
                        sub = (sub + " " + sent).strip()
                    else:
                        if sub:
                            chunks.append(sub)
                        sub = sent
                current = sub
            else:
                current = para

    if current:
        chunks.append(current)

    overlapped: list[str] = []
    for i, chunk in enumerate(chunks):
        if i > 0:
            tail  = chunks[i - 1][-CHUNK_OVERLAP:]
            chunk = tail + " " + chunk
        overlapped.append(chunk.strip())

    return overlapped


# ── Public API ─────────────────────────────────────────────────────────────────

def ingest_document(text: str, doc_id: str) -> dict:
    store = _get_store()

    # Already ingested this session
    if doc_id in store:
        return {"doc_id": doc_id, "chunk_count": len(store[doc_id]["chunks"]), "cached": True}

    chunks = _semantic_chunk(text)
    if not chunks:
        raise ValueError("No chunks produced — document may be empty.")

    embeddings = _embed(chunks)

    store[doc_id] = {"chunks": chunks, "embeddings": embeddings}
    return {"doc_id": doc_id, "chunk_count": len(chunks), "cached": False}


def retrieve(query: str, doc_id: str, top_k: int = TOP_K) -> list[str]:
    store = _get_store()
    if doc_id not in store:
        return []

    query_embedding = _embed([query])[0]
    chunks     = store[doc_id]["chunks"]
    embeddings = store[doc_id]["embeddings"]

    scored = [
        (_cosine_similarity(query_embedding, emb), chunk)
        for emb, chunk in zip(embeddings, chunks)
    ]
    scored.sort(key=lambda x: x[0], reverse=True)

    return [chunk for _, chunk in scored[:top_k]]


def doc_id_from_bytes(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()[:16]
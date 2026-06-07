"""
rag.py — RAG pipeline using Groq embeddings + ChromaDB
Embedding model: nomic-embed-text (via Groq)
Vector store: ChromaDB (in-memory, per session)
"""

import hashlib
import re
from typing import Optional

import chromadb
import streamlit as st
from groq import Groq

# ── Config ─────────────────────────────────────────────────────────────────────

EMBED_MODEL     = "nomic-embed-text-v1_5"   # Groq's hosted embedding model
CHUNK_SIZE      = 800
CHUNK_OVERLAP   = 120
TOP_K           = 6
COLLECTION_NAME = "legalx_policies"


# ── Groq client ────────────────────────────────────────────────────────────────

def _client() -> Groq:
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        raise RuntimeError("GROQ_API_KEY not found in Streamlit secrets.")
    return Groq(api_key=api_key)


# ── ChromaDB (session-scoped via st.session_state) ────────────────────────────

def _get_collection():
    """
    Keep one ChromaDB client + collection per Streamlit session.
    In-memory is fine — documents are re-ingested per session anyway.
    """
    if "chroma_collection" not in st.session_state:
        client = chromadb.Client()
        st.session_state["chroma_collection"] = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    return st.session_state["chroma_collection"]


# ── Groq embeddings ────────────────────────────────────────────────────────────

def _embed(texts: list[str]) -> list[list[float]]:
    """Embed a list of texts using Groq's nomic-embed-text model."""
    client = _client()
    embeddings = []
    # Groq embedding API accepts one text at a time
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

    # Add overlap
    overlapped: list[str] = []
    for i, chunk in enumerate(chunks):
        if i > 0:
            tail  = chunks[i - 1][-CHUNK_OVERLAP:]
            chunk = tail + " " + chunk
        overlapped.append(chunk.strip())

    return overlapped


# ── Public API ─────────────────────────────────────────────────────────────────

def ingest_document(text: str, doc_id: str) -> dict:
    """
    Chunk, embed, and store a document in ChromaDB.
    Skips re-ingestion if the same doc_id is already in the collection.
    """
    col = _get_collection()

    # Check if already ingested this session
    existing = col.get(where={"doc_id": doc_id})
    if existing["ids"]:
        return {"doc_id": doc_id, "chunk_count": len(existing["ids"]), "cached": True}

    chunks = _semantic_chunk(text)
    if not chunks:
        raise ValueError("No chunks produced — document may be empty.")

    embeddings = _embed(chunks)

    ids       = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"doc_id": doc_id, "chunk_index": i} for i in range(len(chunks))]

    col.add(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
    )

    return {"doc_id": doc_id, "chunk_count": len(chunks), "cached": False}


def retrieve(query: str, doc_id: str, top_k: int = TOP_K) -> list[str]:
    """Retrieve the most relevant chunks for a query from a specific document."""
    col = _get_collection()
    query_embedding = _embed([query])[0]

    total = col.count()
    if total == 0:
        return []

    results = col.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, total),
        where={"doc_id": doc_id},
        include=["documents", "distances"],
    )

    return results["documents"][0] if results["documents"] else []


def doc_id_from_bytes(file_bytes: bytes) -> str:
    """Stable document ID from file content hash."""
    return hashlib.sha256(file_bytes).hexdigest()[:16]

"""
rag.py — RAG pipeline using TF-IDF retrieval (no embeddings API needed)
Works entirely with stdlib + streamlit. Perfect for legal/policy documents
which are keyword-dense and respond well to TF-IDF matching.
"""

import hashlib
import math
import re
import string
from collections import Counter

import streamlit as st

# ── Config ─────────────────────────────────────────────────────────────────────

CHUNK_SIZE    = 800
CHUNK_OVERLAP = 120
TOP_K         = 6

# Common English stopwords to ignore during TF-IDF
_STOPWORDS = {
    "a","an","the","and","or","but","in","on","at","to","for","of","with",
    "by","from","is","are","was","were","be","been","being","have","has",
    "had","do","does","did","will","would","could","should","may","might",
    "this","that","these","those","it","its","as","if","not","no","so",
    "we","you","they","he","she","i","my","your","our","their","which","who",
    "what","when","where","how","any","all","each","such","than","then",
    "into","also","shall","upon","per","under","over","above","below",
}


# ── Session-scoped store ───────────────────────────────────────────────────────

def _get_store() -> dict:
    if "vector_store" not in st.session_state:
        st.session_state["vector_store"] = {}
    return st.session_state["vector_store"]


# ── Text preprocessing ─────────────────────────────────────────────────────────

def _tokenize(text: str) -> list[str]:
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    tokens = text.split()
    return [t for t in tokens if t not in _STOPWORDS and len(t) > 2]


# ── TF-IDF ─────────────────────────────────────────────────────────────────────

def _compute_tfidf(chunks: list[str]) -> tuple[list[dict], dict]:
    """
    Returns:
        tf_scores  — per-chunk term frequency dicts
        idf_scores — inverse document frequency dict across all chunks
    """
    tokenized = [_tokenize(c) for c in chunks]
    N = len(chunks)

    # TF: normalised term frequency per chunk
    tf_scores = []
    for tokens in tokenized:
        count = Counter(tokens)
        total = max(len(tokens), 1)
        tf_scores.append({term: freq / total for term, freq in count.items()})

    # IDF: log(N / df) for each term
    df: dict[str, int] = {}
    for token_set in tokenized:
        for term in set(token_set):
            df[term] = df.get(term, 0) + 1

    idf_scores = {term: math.log(N / freq + 1) for term, freq in df.items()}

    return tf_scores, idf_scores


def _tfidf_vector(tf: dict, idf: dict) -> dict:
    return {term: tf_val * idf.get(term, 0) for term, tf_val in tf.items()}


def _cosine_sim(a: dict, b: dict) -> float:
    common = set(a) & set(b)
    if not common:
        return 0.0
    dot    = sum(a[t] * b[t] for t in common)
    mag_a  = math.sqrt(sum(v * v for v in a.values()))
    mag_b  = math.sqrt(sum(v * v for v in b.values()))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


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

    if doc_id in store:
        return {"doc_id": doc_id, "chunk_count": len(store[doc_id]["chunks"]), "cached": True}

    chunks = _semantic_chunk(text)
    if not chunks:
        raise ValueError("No chunks produced — document may be empty.")

    tf_scores, idf_scores = _compute_tfidf(chunks)
    tfidf_vectors = [_tfidf_vector(tf, idf_scores) for tf in tf_scores]

    store[doc_id] = {
        "chunks":         chunks,
        "tfidf_vectors":  tfidf_vectors,
        "idf_scores":     idf_scores,
    }

    return {"doc_id": doc_id, "chunk_count": len(chunks), "cached": False}


def retrieve(query: str, doc_id: str, top_k: int = TOP_K) -> list[str]:
    store = _get_store()
    if doc_id not in store:
        return []

    entry      = store[doc_id]
    idf_scores = entry["idf_scores"]

    # Build query TF-IDF vector
    query_tokens = _tokenize(query)
    query_tf     = Counter(query_tokens)
    total        = max(len(query_tokens), 1)
    query_tf_norm = {t: c / total for t, c in query_tf.items()}
    query_vec    = _tfidf_vector(query_tf_norm, idf_scores)

    # Score each chunk
    scored = [
        (_cosine_sim(query_vec, chunk_vec), chunk)
        for chunk_vec, chunk in zip(entry["tfidf_vectors"], entry["chunks"])
    ]
    scored.sort(key=lambda x: x[0], reverse=True)

    return [chunk for _, chunk in scored[:top_k]]


def doc_id_from_bytes(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()[:16]
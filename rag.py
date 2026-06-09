"""
rag.py — RAG pipeline using LlamaIndex + HuggingFace embeddings + ChromaDB

Stack:
  - Chunking:    LlamaIndex SentenceSplitter
  - Embeddings:  HuggingFace BAAI/bge-small-en-v1.5 (local, no API needed)
  - Vector store: ChromaDB (in-memory, session-scoped)
  - Index:       LlamaIndex VectorStoreIndex
  - Retrieval:   VectorIndexRetriever (cosine similarity)
"""

import hashlib
import streamlit as st

from llama_index.core import VectorStoreIndex, StorageContext, Settings, Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.groq import Groq as GroqLLM

import chromadb

# ── Config ─────────────────────────────────────────────────────────────────────

EMBED_MODEL   = "BAAI/bge-small-en-v1.5"   # ~130MB, runs on CPU, no API needed
LLM_MODEL     = "llama-3.1-8b-instant"
CHUNK_SIZE    = 800
CHUNK_OVERLAP = 120
TOP_K         = 6


# ── Cached embedding model (load once per session) ────────────────────────────

@st.cache_resource(show_spinner="Loading embedding model (first time only)…")
def _get_embed_model():
    """
    Load HuggingFace embedding model once and cache it.
    BAAI/bge-small-en-v1.5 is ~130MB, downloads on first run then cached.
    """
    return HuggingFaceEmbedding(
        model_name=EMBED_MODEL,
        trust_remote_code=True,
    )


def _get_llm():
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        raise RuntimeError("GROQ_API_KEY not found in Streamlit secrets.")
    return GroqLLM(model=LLM_MODEL, api_key=api_key, temperature=0.05)


def _configure_settings():
    Settings.llm         = _get_llm()
    Settings.embed_model = _get_embed_model()
    Settings.chunk_size    = CHUNK_SIZE
    Settings.chunk_overlap = CHUNK_OVERLAP


# ── Session-scoped ChromaDB client ────────────────────────────────────────────

@st.cache_resource
def _get_chroma_client():
    """One ChromaDB in-memory client shared across all sessions on this server."""
    return chromadb.Client()


def _get_store() -> dict:
    if "rag_store" not in st.session_state:
        st.session_state["rag_store"] = {}
    return st.session_state["rag_store"]


# ── Public API ─────────────────────────────────────────────────────────────────

def ingest_document(text: str, doc_id: str) -> dict:
    """
    Chunk, embed, and store a document in ChromaDB via LlamaIndex.

    Flow:
        text → SentenceSplitter → nodes
             → HuggingFaceEmbedding → vectors
             → ChromaVectorStore → VectorStoreIndex
    """
    store = _get_store()

    if doc_id in store:
        return {
            "doc_id": doc_id,
            "chunk_count": store[doc_id]["chunk_count"],
            "cached": True,
        }

    _configure_settings()

    # 1. Wrap text in LlamaIndex Document
    document = Document(text=text, doc_id=doc_id)

    # 2. Sentence-aware chunking
    splitter = SentenceSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        paragraph_separator="\n\n",
    )
    nodes = splitter.get_nodes_from_documents([document])

    if not nodes:
        raise ValueError("No nodes produced — document may be empty.")

    # 3. ChromaDB collection (one per document)
    chroma_client = _get_chroma_client()
    collection = chroma_client.get_or_create_collection(
        name=f"doc_{doc_id}",
        metadata={"hnsw:space": "cosine"},
    )

    # 4. LlamaIndex ChromaVectorStore + StorageContext
    vector_store     = ChromaVectorStore(chroma_collection=collection)
    storage_context  = StorageContext.from_defaults(vector_store=vector_store)

    # 5. Build VectorStoreIndex (embeds nodes and stores in ChromaDB)
    index = VectorStoreIndex(
        nodes,
        storage_context=storage_context,
        embed_model=_get_embed_model(),
        show_progress=False,
    )

    store[doc_id] = {
        "index":       index,
        "chunk_count": len(nodes),
        "collection":  collection,
    }

    return {"doc_id": doc_id, "chunk_count": len(nodes), "cached": False}


def retrieve(query: str, doc_id: str, top_k: int = TOP_K) -> list[str]:
    """
    Retrieve top-k semantically similar chunks using vector similarity search.
    """
    store = _get_store()
    if doc_id not in store:
        return []

    index = store[doc_id]["index"]

    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=top_k,
        embed_model=_get_embed_model(),
    )

    nodes = retriever.retrieve(query)
    return [n.get_content() for n in nodes]


def get_index(doc_id: str):
    """Return the VectorStoreIndex for a document (used by chat engine)."""
    store = _get_store()
    return store.get(doc_id, {}).get("index", None)


def doc_id_from_bytes(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()[:16]
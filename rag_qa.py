"""
rag_qa.py — Conversational Q&A using LlamaIndex CondensePlusContextChatEngine
             backed by ChromaDB VectorStoreIndex + HuggingFace embeddings

Flow per question:
  user question
    → condense with history into standalone query   (Groq LLM)
    → VectorIndexRetriever (cosine sim over ChromaDB)
    → retrieved chunks + history → answer           (Groq LLM)
"""

import streamlit as st

from llama_index.core.chat_engine import CondensePlusContextChatEngine
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.retrievers import VectorIndexRetriever

from rag import get_index, _get_embed_model, _get_llm

# ── System prompt ──────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """You are a plain-English Indian health insurance advisor.
You answer questions about an uploaded health insurance policy document.

RULES:
- Answer using ONLY the retrieved policy context provided to you.
- If the answer is not in the context, say: "This is not mentioned in the uploaded policy."
- Never invent coverage, exclusions, waiting periods, or amounts not in the text.
- Be direct and specific. Quote the clause if it helps.
- Keep answers under 150 words. Write for a layperson — explain any jargon.
- If there is a financial impact, quantify it where possible.
- For follow-up questions, use conversation history to resolve "it", "that", "this"."""


# ── Chat engine (per document, per session) ────────────────────────────────────

def _get_chat_engine(doc_id: str) -> CondensePlusContextChatEngine | None:
    """
    Build or retrieve a CondensePlusContextChatEngine for this document.

    Uses:
      - VectorIndexRetriever over ChromaDB (semantic similarity)
      - HuggingFace embeddings for query encoding
      - Groq LLM for condensing + answering
      - ChatMemoryBuffer for conversation history
    """
    key = f"chat_engine_{doc_id}"
    if key in st.session_state:
        return st.session_state[key]

    index = get_index(doc_id)
    if index is None:
        return None

    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=6,
        embed_model=_get_embed_model(),
    )

    memory = ChatMemoryBuffer.from_defaults(token_limit=3000)

    engine = CondensePlusContextChatEngine.from_defaults(
        retriever=retriever,
        llm=_get_llm(),
        memory=memory,
        system_prompt=_SYSTEM_PROMPT,
        verbose=False,
    )

    st.session_state[key] = engine
    return engine


# ── Public API ─────────────────────────────────────────────────────────────────

def answer_question(
    question: str,
    chunks: list[str],          # kept for API compatibility
    doc_id: str | None = None,
    history: list[dict] | None = None,
) -> str:
    """
    Answer a question using CondensePlusContextChatEngine (primary)
    or fall back to a direct chunk-based prompt if engine is unavailable.
    """
    if doc_id:
        engine = _get_chat_engine(doc_id)
        if engine:
            try:
                response = engine.chat(question)
                return str(response).strip()
            except Exception as e:
                print(f"Chat engine failed, falling back: {e}")

    # Fallback: manual prompt with retrieved chunks
    if not chunks:
        return "I couldn't find relevant clauses in the uploaded policy to answer this."

    from llm import call_llm
    context = "\n\n---\n\n".join(chunks)
    prompt  = f"""{_SYSTEM_PROMPT}

Policy Clauses (retrieved):
{context}

User Question: {question}

Answer:"""
    return call_llm(prompt, timeout=120).strip()


def reset_chat_engine(doc_id: str):
    """Clear the chat engine for a document (called on Clear button)."""
    key = f"chat_engine_{doc_id}"
    if key in st.session_state:
        del st.session_state[key]


def suggest_questions(policy_summary: dict) -> list[str]:
    suggestions = [
        "Does this policy cover pre-existing conditions?",
        "What is the waiting period for heart surgery?",
        "Will my claim be rejected at a non-network hospital?",
        "What's the maximum room rent covered per day?",
        "Does this policy cover maternity expenses?",
        "Are dental treatments covered?",
        "What happens if my treatment cost exceeds the sum insured?",
        "Is there a co-payment for senior citizens?",
    ]

    prioritised = []
    if policy_summary.get("waiting_periods"):
        prioritised.append("What conditions have a waiting period in this policy?")
    if policy_summary.get("co_payment"):
        prioritised.append("Explain the co-payment clause in simple terms.")
    if policy_summary.get("hidden_limits"):
        prioritised.append("What are the sub-limits that reduce my actual payout?")
    if policy_summary.get("exclusions"):
        prioritised.append("List the most important things this policy does NOT cover.")

    for s in suggestions:
        if s not in prioritised:
            prioritised.append(s)

    return prioritised[:6]
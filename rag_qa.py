"""
rag_qa.py — Conversational Q&A over retrieved policy chunks
Uses Llama3 via Ollama with a grounded, citation-aware prompt.
"""

from llm import call_llm

# ── Prompt template ───────────────────────────────────────────────────────────

_QA_PROMPT = """You are a plain-English Indian health insurance advisor.
Answer the user's question using ONLY the policy clauses provided below.

RULES:
- Be direct and specific. Quote the clause if it helps.
- If the answer is not in the clauses, say "This is not mentioned in the uploaded policy."
- Never invent coverage, exclusions, or waiting periods not in the text.
- Keep your answer under 150 words.
- Write for a layperson — no jargon without explanation.
- If there is a financial impact, quantify it where possible.

Policy Clauses (retrieved):
{context}

User Question: {question}

Answer:"""


_HISTORY_PROMPT = """You are a plain-English Indian health insurance advisor.
You are in a conversation with a policyholder about their uploaded policy.

Use ONLY the retrieved policy clauses below to answer.
For follow-up questions, also consider the conversation history.

RULES:
- Direct, specific, under 150 words.
- Cite the policy text when useful.
- If the answer is not in the clauses, say "This is not mentioned in the uploaded policy."
- Never invent terms not present in the text.

Conversation History:
{history}

Retrieved Policy Clauses:
{context}

User Question: {question}

Answer:"""


# ── Public API ────────────────────────────────────────────────────────────────

def answer_question(
    question: str,
    chunks: list[str],
    history: list[dict] | None = None,
) -> str:
    """
    Answer a question grounded in retrieved policy chunks.

    Args:
        question: User's natural language question
        chunks:   Retrieved chunks from rag.retrieve()
        history:  Optional list of {"role": "user"|"assistant", "content": str}

    Returns:
        Answer string from the LLM
    """
    if not chunks:
        return (
            "I couldn't find relevant clauses in the uploaded policy to answer this. "
            "Try rephrasing your question or check if the policy covers this topic."
        )

    context = "\n\n---\n\n".join(chunks)

    if history:
        # Format conversation history
        history_text = "\n".join(
            f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
            for m in history[-6:]  # last 3 turns to stay within context
        )
        prompt = _HISTORY_PROMPT.format(
            history=history_text,
            context=context,
            question=question,
        )
    else:
        prompt = _QA_PROMPT.format(context=context, question=question)

    return call_llm(prompt, timeout=120).strip()


def suggest_questions(policy_summary: dict) -> list[str]:
    """
    Generate contextual suggested questions based on what was found in the policy.
    Helps users know what to ask.
    """
    suggestions = [
        "Does this policy cover pre-existing conditions?",
        "What is the waiting period for heart surgery?",
        "Will my claim be rejected if I'm admitted to a non-network hospital?",
        "What's the maximum room rent covered per day?",
        "Does this policy cover maternity expenses?",
        "Are dental treatments covered?",
        "What happens if my treatment cost exceeds the sum insured?",
        "Is there a co-payment for senior citizens?",
    ]

    # Prioritise based on what the LLM actually found
    prioritised = []

    if policy_summary.get("waiting_periods"):
        prioritised.append("What conditions have a waiting period in this policy?")

    if policy_summary.get("co_payment"):
        prioritised.append("Explain the co-payment clause in simple terms.")

    if policy_summary.get("hidden_limits"):
        prioritised.append("What are the sub-limits that reduce my actual payout?")

    if policy_summary.get("exclusions"):
        prioritised.append("List the most important things this policy does NOT cover.")

    # Fill remaining slots from generic list
    for s in suggestions:
        if s not in prioritised:
            prioritised.append(s)

    return prioritised[:6]

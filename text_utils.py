def chunk_text(text, chunk_size=3000):
    """
    Splits long legal documents into
    LLM-readable chunks.
    """
    chunks = []

    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])

    return chunks
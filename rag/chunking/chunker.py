def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[tuple[str, str]]:
    """Split *text* into overlapping chunks.
    Returns a list of (chunk_id, chunk_text) where *chunk_id* is a simple
    ``f"{i}"`` string representing the chunk order.
    The function operates on whitespace‑separated tokens, approximating a token
    count by word count.
    """
    tokens = text.split()
    if not tokens:
        return []
    chunks = []
    i = 0
    while i < len(tokens):
        start = i
        end = min(i + chunk_size, len(tokens))
        chunk_tokens = tokens[start:end]
        chunk_text = " ".join(chunk_tokens)
        chunk_id = f"{start}_{end}"
        chunks.append((chunk_id, chunk_text))
        # Advance by chunk_size - overlap for next window
        i += chunk_size - overlap
    return chunks

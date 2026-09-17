import hashlib
from typing import List

def _hash_to_floats(text: str, dim: int = 128) -> List[float]:
    """Deterministic pseudo-embedding: hash the text and expand to a fixed-length float list.
    This avoids heavy model dependencies while providing repeatable vectors for tests.
    """
    # Use SHA256 hash, repeat as needed to fill dim
    h = hashlib.sha256(text.encode('utf-8')).digest()
    # Convert bytes to ints 0-255, then normalize to 0-1 float
    ints = [b for b in h]
    # Repeat pattern to reach desired dimension
    repeats = (dim + len(ints) - 1) // len(ints)
    vals = (ints * repeats)[:dim]
    return [v / 255.0 for v in vals]

def embed_text(text: str) -> List[float]:
    """Public API to embed a piece of text.
    For production you would replace this with a real sentence‑embedding model.
    """
    return _hash_to_floats(text)

import numpy as np
from typing import List, Dict, Any

def _cosine_similarity(a: List[float], b: List[float]) -> float:
    a_arr = np.array(a)
    b_arr = np.array(b)
    if np.linalg.norm(a_arr) == 0 or np.linalg.norm(b_arr) == 0:
        return 0.0
    return float(np.dot(a_arr, b_arr) / (np.linalg.norm(a_arr) * np.linalg.norm(b_arr)))

def rerank(query_emb: List[float], docs: List[str], metadatas: List[Dict[str, Any]], k: int = 3) -> List[Dict[str, Any]]:
    """Lightweight reranker that sorts documents by cosine similarity to the query embedding.
    Returns the top‑k items as dictionaries containing ``text`` and ``metadata``.
    """
    scores = [_cosine_similarity(query_emb, embed_text(doc)) for doc in docs]
    # Attach scores to each entry
    entries = [
        {"text": doc, "metadata": meta, "score": score}
        for doc, meta, score in zip(docs, metadatas, scores)
    ]
    # Sort descending by score
    entries.sort(key=lambda x: x["score"], reverse=True)
    # Return top‑k (strip score)
    return [{"text": e["text"], "metadata": e["metadata"]} for e in entries[:k]]

# Helper to embed text (re‑use the same deterministic embedder as in rag.embeddings)
from rag.embeddings.embedder import embed_text

import json
import os
from pathlib import Path
from typing import List, Dict, Any

import chromadb
from rag.embeddings.embedder import embed_text
from backend.core.config import settings

# Path to the ChromaDB persistent storage (shared with voice_embeddings)
_VECTOR_DB_PATH = settings.VECTOR_DB_PATH

def _get_collection() -> Any:
    client = chromadb.PersistentClient(path=_VECTOR_DB_PATH)
    return client.get_or_create_collection(
        name="clinical_evidence",
        metadata={"description": "Trusted clinical evidence embeddings"}
    )

def _build_query_text(prediction: Dict[str, Any], structured_evidence: Dict[str, Any]) -> str:
    """Construct a simple textual query from prediction and structured evidence.
    • Uses the predicted label / probability.
    • Includes top SHAP feature names if available.
    """
    parts = []
    # Prediction label and confidence
    label = prediction.get("label") or prediction.get("prediction")
    confidence = prediction.get("confidence") or prediction.get("probability")
    if label:
        parts.append(str(label))
    if confidence:
        parts.append(f"confidence {confidence}")
    # Structured evidence – we expect a list of SHAP features
    shap = structured_evidence.get("shap_features") or []
    if isinstance(shap, list) and shap:
        # take top 3 feature names (assuming each entry is {'feature': ..., 'value': ...})
        top_features = [f.get("feature") for f in shap[:3] if isinstance(f, dict)]
        parts.extend([str(f) for f in top_features if f])
    # Fallback if nothing else
    if not parts:
        parts.append("clinical Parkinson voice")
    return " ".join(parts)

import time
from backend.core.logging import log_rag_retrieval

def retrieve_evidence(prediction: Dict[str, Any], structured_evidence: Dict[str, Any], k: int = 3, session_id: str = "session_rag") -> List[Dict[str, Any]]:
    """Retrieve the top‑k clinical evidence chunks relevant to a session.

    Returns a list of dictionaries containing:
        - ``id``: Chroma vector id (``{source_id}_{chunk_id}``)
        - ``text``: The raw chunk text
        - ``metadata``: The metadata stored with the chunk (source_title, source_type, …)
    """
    start_time = time.perf_counter()
    collection = _get_collection()
    query_text = _build_query_text(prediction, structured_evidence)
    # Use deterministic embedder for the query
    query_emb = embed_text(query_text)
    # Query Chroma – we pass the embedding directly for reproducibility
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=k,
        include=["ids", "documents", "metadatas"]
    )
    # Chromadb returns lists of lists (one per query). We only have one query.
    ids = results.get("ids", [[]])[0]
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    retrieved = []
    for vid, doc, meta in zip(ids, docs, metas):
        retrieved.append({
            "id": vid,
            "text": doc,
            "metadata": meta,
        })

    duration_ms = (time.perf_counter() - start_time) * 1000.0
    log_rag_retrieval(
        session_id=session_id,
        query_text=query_text,
        latency_ms=duration_ms,
        chunks_retrieved=len(retrieved),
    )

    return retrieved

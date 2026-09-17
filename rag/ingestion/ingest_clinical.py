import os
from pathlib import Path
import chromadb
from backend.core.config import settings
from rag.ingestion.verify_sources import verify_source
from rag.ingestion.fetch_sources import load_source_content
from rag.chunking.chunker import chunk_text
from rag.embeddings.embedder import embed_text

# Path to metadata JSON
_METADATA_PATH = Path(__file__).resolve().parents[1] / "schemas" / "document_metadata.json"

def load_source_metadata(source_id: str) -> dict:
    import json
    with open(_METADATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    for src in data.get("approved_sources", []):
        if src.get("source_id") == source_id:
            return src
    raise ValueError(f"Metadata for source '{source_id}' not found")

def ingest_source(source_id: str):
    """Ingest a single approved source into the clinical_evidence vector store.
    Raises if the source is not approved.
    """
    # Verify approval
    verify_source(source_id)
    # Load metadata
    meta = load_source_metadata(source_id)
    title = meta.get("title", "")
    source_type = meta.get("source_type", "")
    # Load raw text
    raw_text = load_source_content(source_id)
    # Chunk
    chunks = chunk_text(raw_text)
    # Prepare embeddings and metadata
    embeddings = []
    ids = []
    metadatas = []
    for chunk_id, chunk in chunks:
        embeddings.append(embed_text(chunk))
        ids.append(f"{source_id}_{chunk_id}")
        metadatas.append({
            "source_title": title,
            "chunk_id": chunk_id,
            "source_type": source_type,
            "source_id": source_id,
        })
    # Store in Chroma collection
    client = chromadb.PersistentClient(path=settings.VECTOR_DB_PATH)
    collection = client.get_or_create_collection(
        name="clinical_evidence",
        metadata={"description": "Trusted clinical evidence embeddings"}
    )
    collection.add(embeddings=embeddings, ids=ids, metadatas=metadatas)
    return len(chunks)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: ingest_clinical.py <source_id>")
        sys.exit(1)
    count = ingest_source(sys.argv[1])
    print(f"Ingested {count} chunks for source {sys.argv[1]}")

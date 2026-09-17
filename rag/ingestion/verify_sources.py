import json
import os
from pathlib import Path
from typing import List, Dict

# Load approved sources metadata
_METADATA_PATH = Path(__file__).resolve().parents[1] / "schemas" / "document_metadata.json"

def load_metadata() -> List[Dict]:
    if not _METADATA_PATH.exists():
        raise FileNotFoundError(f"Metadata file not found at {_METADATA_PATH}")
    with open(_METADATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("approved_sources", [])

def is_approved(source_id: str) -> bool:
    """Check whether a given source_id is present in the approved list."""
    approved = load_metadata()
    return any(src.get("source_id") == source_id for src in approved)

def verify_source(source_id: str) -> None:
    """Raise an exception if the source is not approved.
    
    Used by the ingestion pipeline to enforce strict source control.
    """
    if not is_approved(source_id):
        raise ValueError(f"Source '{source_id}' is not in the approved list and cannot be ingested.")

if __name__ == "__main__":
    # Simple CLI for manual testing
    import sys
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <source_id>")
        sys.exit(1)
    try:
        verify_source(sys.argv[1])
        print(f"Source '{sys.argv[1]}' is approved.")
    except Exception as e:
        print(str(e))
        sys.exit(1)

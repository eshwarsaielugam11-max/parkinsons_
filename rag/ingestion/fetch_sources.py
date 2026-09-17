import os
import json
from pathlib import Path
from typing import List, Tuple

def load_sources_dir() -> Path:
    """Return the directory where raw source text files are stored."""
    # Expected layout: rag/sources/<source_id>.txt
    return Path(__file__).resolve().parents[2] / "sources"

def load_source_content(source_id: str) -> str:
    src_dir = load_sources_dir()
    file_path = src_dir / f"{source_id}.txt"
    if not file_path.exists():
        raise FileNotFoundError(f"Source file {file_path} not found")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    # Simple CLI for debugging
    import sys
    if len(sys.argv) != 2:
        print("Usage: fetch_sources.py <source_id>")
        sys.exit(1)
    print(load_source_content(sys.argv[1]))

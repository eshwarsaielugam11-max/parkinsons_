import json
from typing import Dict, Any, List

from backend.rag.retriever import retrieve_evidence

# Hand‑written test queries with expected thematic keywords (for manual inspection)
TEST_QUERIES = [
    {
        "name": "jitter_shimmer",
        "prediction": {"label": "Parkinson", "confidence": 0.88},
        "structured_evidence": {"shap_features": [{"feature": "jitter"}, {"feature": "shimmer"}]},
        "k": 3,
    },
    {
        "name": "speech_rate",
        "prediction": {"label": "Parkinson", "confidence": 0.75},
        "structured_evidence": {"shap_features": [{"feature": "speech_rate"}]},
        "k": 2,
    },
]

def run_evaluation():
    for q in TEST_QUERIES:
        print(f"=== Query: {q['name']} ===")
        results = retrieve_evidence(q["prediction"], q["structured_evidence"], k=q["k"])
        for i, r in enumerate(results, 1):
            meta = r.get("metadata", {})
            print(f"Chunk {i}: source_title={meta.get('source_title')} source_type={meta.get('source_type')}")
            print(f"   text: {r.get('text')[:120]}...\n")
        print("---\n")

if __name__ == "__main__":
    run_evaluation()

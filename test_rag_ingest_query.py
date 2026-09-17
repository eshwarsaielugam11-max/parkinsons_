import os
from rag.ingestion.verify_sources import load_approved_sources
from rag.ingestion.fetch_sources import fetch_document_content
from rag.chunking.chunker import chunk_text
from rag.embeddings.embedder import clinical_index

def run_ingestion_and_query():
    approved_sources = load_approved_sources()
    all_chunks = []
    
    for source_id, metadata in approved_sources.items():
        text = fetch_document_content(source_id, metadata)
        chunks = chunk_text(text, source_id, metadata)
        all_chunks.extend(chunks)
        
    print(f"Ingesting {len(all_chunks)} chunks...")
    clinical_index.add_chunks(all_chunks)
    
    query = "What voice biomarkers are used for Parkinson's classification?"
    print(f"\nQuerying: '{query}'")
    
    results = clinical_index.query(query, k=2)
    for i, res in enumerate(results):
        print(f"\nResult {i+1}:")
        print(f"Source: {res['metadata'].get('title')} ({res['metadata'].get('year')})")
        print(f"Text snippet: {res['text']}")
        print(f"Distance: {res['distance']:.4f}")

if __name__ == "__main__":
    run_ingestion_and_query()

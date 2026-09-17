import os
import chromadb
from typing import List, Dict, Optional
from backend.core.config import settings

class VoiceSimilarityIndex:
    """
    Manages the isolated ChromaDB vector index storing deep voice-representation
    embeddings (from Phase 12's pooled Transformer output).
    
    WARNING: Kept strictly separate from the clinical-evidence vector store (Phase 35).
    All matches must be labeled as 'similar recorded voice patterns' only.
    """
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = settings.VECTOR_DB_PATH
            
        os.makedirs(db_path, exist_ok=True)
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Dedicated collection
        self.collection = self.client.get_or_create_collection(
            name="voice_embeddings",
            metadata={"description": "Similar recorded voice patterns (Not diagnostic evidence)"}
        )
        
    def add_voice_embedding(
        self, 
        session_id: str, 
        embedding: List[float], 
        patient_id: Optional[str] = None, 
        label: Optional[int] = None
    ):
        """
        Stores the pooled deep-representation embedding for nearest-neighbor similarity retrieval.
        """
        metadata = {"session_id": session_id}
        if patient_id is not None:
            metadata["patient_id"] = patient_id
        if label is not None:
            metadata["label"] = label
            
        self.collection.add(
            embeddings=[embedding],
            metadatas=[metadata],
            ids=[session_id]
        )
        
    def find_similar(self, embedding: List[float], k: int = 5) -> List[Dict]:
        """
        Queries nearest neighbors.
        Explicitly enforces RESEARCH_CONSTRAINTS item 10 labeling.
        """
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=k
        )
        
        similar_sessions = []
        
        if not results["ids"] or not results["ids"][0]:
            return similar_sessions
            
        for i in range(len(results["ids"][0])):
            session_id = results["ids"][0][i]
            dist = results["distances"][0][i] if results["distances"] else 0.0
            meta = results["metadatas"][0][i] if results["metadatas"] else {}
            
            similar_sessions.append({
                "session_id": session_id,
                "distance": dist,
                "metadata": meta,
                "similarity_type": "similar recorded voice patterns",
                "disclaimer": "WARNING: Not diagnostic evidence."
            })
            
        return similar_sessions

# Singleton instance
voice_index = VoiceSimilarityIndex()

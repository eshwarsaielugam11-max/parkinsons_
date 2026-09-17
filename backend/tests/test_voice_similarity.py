import pytest
import os
import shutil
from backend.retrieval.voice_similarity import VoiceSimilarityIndex

@pytest.fixture(scope="module")
def similarity_index():
    test_db_path = "./test_chroma_db"
    if os.path.exists(test_db_path):
        shutil.rmtree(test_db_path)
    
    index = VoiceSimilarityIndex(db_path=test_db_path)
    yield index
    
    # Cleanup
    if os.path.exists(test_db_path):
        shutil.rmtree(test_db_path)

def test_voice_similarity_retrieval(similarity_index):
    # Base embedding
    base_emb = [0.1, 0.2, 0.3, 0.4]
    
    # Add varying distances
    # Very close
    similarity_index.add_voice_embedding("sess_close", [0.11, 0.21, 0.31, 0.41], "pat_1", 1)
    # Far
    similarity_index.add_voice_embedding("sess_far", [0.9, 0.9, 0.9, 0.9], "pat_2", 0)
    # Medium
    similarity_index.add_voice_embedding("sess_medium", [0.5, 0.5, 0.5, 0.5], "pat_3", 1)
    
    results = similarity_index.find_similar(base_emb, k=3)
    
    # Assert return format and constraints
    assert len(results) == 3
    
    # Nearest should be sess_close
    assert results[0]["session_id"] == "sess_close"
    assert results[1]["session_id"] == "sess_medium"
    assert results[2]["session_id"] == "sess_far"
    
    # Assert disclaimer presence
    assert results[0]["similarity_type"] == "similar recorded voice patterns"
    assert "Not diagnostic evidence" in results[0]["disclaimer"]
    
    # Assert metadata retrieval
    assert results[0]["metadata"]["patient_id"] == "pat_1"
    assert results[0]["metadata"]["label"] == 1

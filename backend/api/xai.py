from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from backend.schemas.xai import StructuredEvidenceResponse
from backend.database.session_db import get_db
from backend.models import Report

import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import Phase 18 module
from model.src.explainability.evidence_schema import create_structured_evidence

router = APIRouter()

@router.get("/{session_id}", response_model=StructuredEvidenceResponse)
async def get_xai(session_id: str, db: Session = Depends(get_db)):
    """
    Retrieve structured explainability evidence for a given prediction session.
    The response payload directly powers the frontend XAI components (Phase 44).
    """
    report = db.query(Report).filter(Report.session_id == session_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found."
        )
        
    refs = report.structured_evidence
    
    if not refs or "acoustic_shap_values" not in refs or not refs["acoustic_shap_values"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"XAI data not generated for session {session_id}."
        )
        
    evidence_dict = create_structured_evidence(
        session_id=session_id,
        probability=report.prediction.get("pd_probability_calibrated", 0.0),
        confidence=report.prediction.get("confidence_score", 0.0),
        quality_score=report.prediction.get("audio_quality_score", 0.0),
        acoustic_shap=refs.get("acoustic_shap_values", {}),
        shap_base_value=0.5,
        temporal_importance=refs.get("temporal_attention", []),
        spectrogram_heatmap_path=refs.get("gradcam_heatmap_path", "")
    )
    
    return StructuredEvidenceResponse(**evidence_dict)

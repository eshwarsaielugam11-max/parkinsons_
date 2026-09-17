from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from backend.schemas.prediction import StoredPrediction, PatientHistoryResponse, PredictionResponse, PredictionScore, ExplanationRefs
from backend.database.session_db import get_db
from backend.models import Report, Session as DbSession

router = APIRouter()

@router.get("/{session_id}", response_model=StoredPrediction)
async def get_prediction(session_id: str, db: Session = Depends(get_db)):
    """
    Retrieve a previously computed session prediction directly from the Postgres database.
    """
    report = db.query(Report).filter(Report.session_id == session_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction session {session_id} not found."
        )
        
    db_session = report.session
        
    prediction_data = PredictionScore(**report.prediction)
    explanation_refs = ExplanationRefs(**report.structured_evidence) if report.structured_evidence else ExplanationRefs()
    
    return StoredPrediction(
        session_id=session_id,
        patient_id=db_session.patient_id,
        timestamp=db_session.timestamp,
        result=PredictionResponse(
            prediction=prediction_data,
            explanation_refs=explanation_refs
        )
    )

@router.get("/patients/{patient_id}/history", response_model=PatientHistoryResponse)
async def get_patient_history(patient_id: str, db: Session = Depends(get_db)):
    """
    Retrieve chronological prediction history for a given patient from Postgres.
    """
    sessions = db.query(DbSession).filter(DbSession.patient_id == patient_id).order_by(DbSession.timestamp.asc()).all()
    
    history = []
    for s in sessions:
        if s.report:
            prediction_data = PredictionScore(**s.report.prediction)
            explanation_refs = ExplanationRefs(**s.report.structured_evidence) if s.report.structured_evidence else ExplanationRefs()
            
            history.append(
                StoredPrediction(
                    session_id=s.id,
                    patient_id=s.patient_id,
                    timestamp=s.timestamp,
                    result=PredictionResponse(
                        prediction=prediction_data,
                        explanation_refs=explanation_refs
                    )
                )
            )
            
    return PatientHistoryResponse(
        patient_id=patient_id,
        history=history
    )

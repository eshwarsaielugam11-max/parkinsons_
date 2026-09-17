from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Depends
import tempfile
import os
import uuid
from typing import Optional
from sqlalchemy.orm import Session
from backend.inference.predictor_service import predict_with_embedding
from backend.schemas.prediction import PredictionResponse
from backend.database.session_db import get_db
from backend.models import Patient, Session as DbSession, Recording, Report
from backend.retrieval.voice_similarity import voice_index
from backend.core.security import sanitize_user_text
from datetime import datetime, timezone

router = APIRouter()

MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB
ALLOWED_CONTENT_TYPES = {
    "audio/wav", "audio/x-wav", "audio/wave",
    "audio/mpeg", "audio/mp3", "audio/x-mp3",
    "audio/mp4", "audio/x-m4a", "audio/m4a", "audio/aac",
    "application/octet-stream"
}
ALLOWED_EXTENSIONS = {".wav", ".mp3", ".m4a", ".mp4"}

@router.post("", response_model=PredictionResponse)
async def upload_audio(
    file: UploadFile = File(...),
    patient_id: Optional[str] = Form(None),
    label: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    patient_id = sanitize_user_text(patient_id) if patient_id else None
    
    # Check mime type and file extension
    file_ext = os.path.splitext(file.filename or "")[1].lower()
    if file.content_type not in ALLOWED_CONTENT_TYPES and file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file.content_type} (extension: {file_ext})"
        )
        
    temp_path = None
    try:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        temp_path = temp_file.name
        temp_file.close()
        
        file_size = 0
        with open(temp_path, "wb") as buffer:
            while chunk := await file.read(8192):
                file_size += len(chunk)
                if file_size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                        detail="File exceeds maximum size of 25MB"
                    )
                buffer.write(chunk)
                
        # Perform inference
        prediction, embedding = predict_with_embedding(temp_path, return_explanations=True)
        
        # Write to DB if patient_id is provided
        session_id = str(uuid.uuid4())
        if patient_id:
            # Ensure patient exists
            patient = db.query(Patient).filter(Patient.id == patient_id).first()
            if not patient:
                patient = Patient(id=patient_id)
                db.add(patient)
                
            db_session = DbSession(id=session_id, patient_id=patient_id, task_type="upload", mode="upload", timestamp=datetime.now(timezone.utc))
            db.add(db_session)
            
            db_report = Report(
                id=str(uuid.uuid4()),
                session_id=session_id,
                prediction=prediction.prediction.model_dump(),
                structured_evidence=prediction.explanation_refs.model_dump(),
                model_version="1.0.0"
            )
            db.add(db_report)
            db.commit()
            
        # Write to Voice Similarity Index
        if embedding:
            voice_index.add_voice_embedding(
                session_id=session_id,
                embedding=embedding,
                patient_id=patient_id,
                label=label
            )
            
        return prediction
        
    finally:
        # Guarantee cleanup even on exception
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

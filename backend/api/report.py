import logging
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from backend.database.session_db import get_db
from backend.models import Report as DbReport, Session as DbSession
from backend.rag.llm_client import generate_report
from backend.rag.output_validator import ReportValidator
from backend.schemas.report import RetrievedClinicalEvidence

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/{session_id}")
@router.get("/{session_id}")
async def generate_report_endpoint(session_id: str, db: Session = Depends(get_db)):
    """Generate a validated report for a given session.

    Workflow:
    1. Load stored prediction and structured evidence.
    2. Call the LLM to produce a raw report.
    3. Validate the report against ``ReportSchema``.
    4. If validation fails, retry once with a correction instruction.
    5. If it still fails, return HTTP 500 with a clear error message.
    """
    # Retrieve the persisted report record
    db_report = db.query(DbReport).filter(DbReport.session_id == session_id).first()
    if not db_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report for session {session_id} not found.",
        )

    # Extract prediction and structured evidence JSON blobs (may be None)
    prediction = db_report.prediction or {}
    structured_evidence = db_report.structured_evidence or {}

    # Placeholder: similarity results and retrieved clinical evidence are not persisted yet.
    similarity_results = []
    retrieved_evidence: list[RetrievedClinicalEvidence] = []

    try:
        # First LLM call
        raw_report = generate_report(
            prediction=prediction,
            structured_evidence=structured_evidence,
            retrieved_chunks=[],
            similarity_results=similarity_results,
            audio_quality_score=prediction.get("audio_quality_score", 0.0),
        )

        expected_prob = (
            prediction.get("calibrated_probability")
            or prediction.get("probability")
            or 0.0
        )

        try:
            validated = ReportValidator.validate(
                report_text=raw_report,
                expected_calibrated_probability=float(expected_prob),
                retrieved_evidence=retrieved_evidence,
            )
            return {"report": raw_report, "validated": validated.dict()}
        except Exception as exc:
            logger.warning("Report validation failed on first attempt: %s", exc)
            # Retry once – the LLM is prompted to correct numeric mismatches.
            raw_report_retry = generate_report(
                prediction=prediction,
                structured_evidence=structured_evidence,
                retrieved_chunks=[],
                similarity_results=similarity_results,
                audio_quality_score=prediction.get("audio_quality_score", 0.0),
            )
            validated = ReportValidator.validate(
                report_text=raw_report_retry,
                expected_calibrated_probability=float(expected_prob),
                retrieved_evidence=retrieved_evidence,
            )
            return {"report": raw_report_retry, "validated": validated.dict()}
    except Exception as exc:
        logger.error("Report generation/validation failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Report generation degraded – numeric results only.",
        )

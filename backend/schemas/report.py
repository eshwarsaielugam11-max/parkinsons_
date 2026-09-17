from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field, validator


class RetrievedClinicalEvidence(BaseModel):
    """Metadata for a clinical evidence chunk that was retrieved.

    Only the fields required for citation checks are included.
    """

    source_title: str = Field(..., description="Title of the source document")
    # Additional optional metadata can be added later.
    metadata: Optional[dict[str, Any]] = Field(default=None)


class ReportSchema(BaseModel):
    """Full report schema returned by the `/api/v1/report/{session_id}` endpoint.

    Mirrors the master specification (Section 22). All fields are kept as simple as possible
    while still providing strong typing for the frontend.
    """

    session_id: str = Field(..., description="Unique identifier for the session")
    patient_id: Optional[str] = Field(
        None, description="Identifier for the patient (if permitted to expose)"
    )
    timestamp: datetime = Field(..., description="Report generation timestamp (ISO‑8601)")
    model_version: str = Field(..., description="Version tag of the model used for inference")
    screening_result: str = Field(..., description="High‑level result, e.g. 'Positive' or 'Negative'")
    calibrated_probability: float = Field(..., ge=0.0, le=1.0, description="Calibrated PD probability")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence score")
    audio_quality: float = Field(..., ge=0.0, le=1.0, description="Audio quality score (0‑1)")
    major_acoustic_findings: List[str] = Field(
        default_factory=list,
        description="Key acoustic phenomena identified (e.g., jitter, shimmer)",
    )
    asr_findings: List[str] = Field(
        default_factory=list,
        description="Any Automatic Speech Recognition observations",
    )
    relevant_time_intervals: List[dict[str, Any]] = Field(
        default_factory=list,
        description="Time windows (in seconds) that are clinically relevant",
    )
    spectrogram_explanation_refs: List[str] = Field(
        default_factory=list,
        description="References (file paths or URLs) to spectrogram/Grad‑CAM images",
    )
    shap_findings: List[Any] = Field(
        default_factory=list,
        description="SHAP per‑feature signed values; concrete shape is backend‑specific",
    )
    temporal_findings: List[Any] = Field(
        default_factory=list,
        description="Temporal attention‑rollout scores per window",
    )
    similar_voice_evidence: List[Any] = Field(
        default_factory=list,
        description="Results from the voice‑similarity retrieval layer",
    )
    retrieved_clinical_evidence: List[RetrievedClinicalEvidence] = Field(
        default_factory=list,
        description="Clinical evidence chunks that were used to ground the report",
    )
    limitations: str = Field(..., description="Any limitations of the model or data")
    clinical_recommendation: str = Field(..., description="Suggested next steps for the clinician")
    disclaimer: str = Field(
        ...,
        description="Mandatory legal disclaimer. Must match the exact wording required by the spec.",
    )

    @validator("disclaimer")
    def disclaimer_must_match(cls, v: str) -> str:
        required = (
            "THIS IS AN AI‑BASED SCREENING/DECISION‑SUPPORT OUTPUT, NOT A STANDALONE DIAGNOSIS."
        )
        if v.strip() != required:
            raise ValueError("Report disclaimer does not match required wording")
        return v

    class Config:
        orm_mode = True
        anystr_strip_whitespace = True

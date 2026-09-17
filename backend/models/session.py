from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .base import Base

class Session(Base):
    """
    Core interaction recording for a patient (e.g. one clinical visit or app usage block).
    """
    __tablename__ = 'sessions'
    
    id = Column(String, primary_key=True)
    patient_id = Column(String, ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    
    task_type = Column(String, nullable=False) # e.g. "read_text", "free_speech", "sustained_vowel"
    mode = Column(String, nullable=False) # e.g. "upload", "stream"

    # Relationships
    patient = relationship("Patient", back_populates="sessions")
    recordings = relationship("Recording", back_populates="session", cascade="all, delete-orphan")
    report = relationship("Report", back_populates="session", uselist=False, cascade="all, delete-orphan")

from sqlalchemy import Column, String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .base import Base

class Report(Base):
    """
    Stores the final immutable prediction and explainability artifacts for a session.
    """
    __tablename__ = 'reports'
    
    id = Column(String, primary_key=True)
    # One-to-one relationship with Session
    session_id = Column(String, ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False, unique=True)
    
    prediction = Column(JSON, nullable=True)
    structured_evidence = Column(JSON, nullable=True)
    generated_report_text = Column(String, nullable=True)
    model_version = Column(String, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    session = relationship("Session", back_populates="report")

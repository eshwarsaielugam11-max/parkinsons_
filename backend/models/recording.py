from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Recording(Base):
    """
    Tracks raw audio artifacts associated with a session.
    """
    __tablename__ = 'recordings'
    
    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False)
    storage_ref = Column(String, nullable=False) # e.g. "s3://bucket/path/to/file.wav"
    audio_quality_score = Column(Float, nullable=True)
    
    # Allows scheduled jobs to scrub raw audio to comply with data minimization
    retention_expires_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    session = relationship("Session", back_populates="recordings")

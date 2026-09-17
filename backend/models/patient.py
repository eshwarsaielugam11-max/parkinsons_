from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from .base import Base

class Patient(Base):
    """
    Patient identity and demographic model.
    Note: Free-text identifying fields (e.g. name, exact DOB, contact info) are
    intentionally omitted per the master spec privacy requirements.
    """
    __tablename__ = 'patients'
    
    id = Column(String, primary_key=True)
    age_bucket = Column(String, nullable=True) # e.g. "60-69"
    sex = Column(String, nullable=True) # e.g. "M", "F", "O"
    
    # Relationships
    # If a patient is deleted (e.g., GDPR/HIPAA request), cascade deletes all sessions
    sessions = relationship("Session", back_populates="patient", cascade="all, delete-orphan")

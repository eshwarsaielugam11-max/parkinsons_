import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone, timedelta
from backend.models import Base, Patient, Session, Recording, Report

@pytest.fixture(scope="module")
def engine():
    # Use in-memory SQLite for testing models
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture(scope="function")
def db_session(engine):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

def test_patient_session_relationship(db_session):
    p = Patient(id="patient_1", age_bucket="60-69", sex="M")
    s = Session(id="session_1", patient=p, task_type="read_text", mode="upload")
    
    db_session.add(p)
    db_session.commit()
    
    # Test navigation
    assert p.sessions[0].id == "session_1"
    assert s.patient.id == "patient_1"

def test_full_model_hierarchy_and_cascades(db_session):
    # Setup
    p = Patient(id="patient_2", age_bucket="70-79", sex="F")
    s = Session(id="session_2", patient=p, task_type="free_speech", mode="stream")
    
    expire_time = datetime.now(timezone.utc) + timedelta(days=7)
    r = Recording(id="recording_1", session=s, storage_ref="s3://test/rec.wav", audio_quality_score=9.5, retention_expires_at=expire_time)
    
    rep = Report(id="report_1", session=s, prediction={"pd": 0.8}, structured_evidence={"xai": True}, generated_report_text="Test", model_version="v1.0.0")
    
    db_session.add(p)
    db_session.commit()
    
    # Assert models saved correctly
    assert len(p.sessions) == 1
    assert p.sessions[0].recordings[0].storage_ref == "s3://test/rec.wav"
    assert p.sessions[0].report.prediction == {"pd": 0.8}
    
    # Delete Patient -> should cascade delete session, recording, report
    db_session.delete(p)
    db_session.commit()
    
    # Verify everything is gone
    assert db_session.query(Patient).filter_by(id="patient_2").count() == 0
    assert db_session.query(Session).filter_by(id="session_2").count() == 0
    assert db_session.query(Recording).filter_by(id="recording_1").count() == 0
    assert db_session.query(Report).filter_by(id="report_1").count() == 0

def test_print_ddl():
    from sqlalchemy.schema import CreateTable
    from sqlalchemy.dialects import sqlite
    print("\n--- DDL ---")
    for table in Base.metadata.sorted_tables:
        print(CreateTable(table).compile(dialect=sqlite.dialect()))
    print("-----------")

from fastapi import APIRouter, Depends
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import text
import chromadb

from backend.core.config import settings
from backend.database.session_db import get_db

router = APIRouter()

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint reporting overall service status, model version,
    relational database connectivity, and vector DB status.
    """
    # 1. Relational DB check
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        db_status = f"unreachable: {str(exc)}"

    # 2. Vector DB check
    vector_status = "connected"
    try:
        chroma_client = chromadb.PersistentClient(path=settings.VECTOR_DB_PATH)
        chroma_client.heartbeat()
    except Exception as exc:
        vector_status = f"unreachable: {str(exc)}"

    overall_healthy = (db_status == "connected" and vector_status == "connected")

    return {
        "status": "healthy" if overall_healthy else "degraded",
        "model_version": settings.MODEL_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": {
            "database": db_status,
            "vector_db": vector_status,
        }
    }

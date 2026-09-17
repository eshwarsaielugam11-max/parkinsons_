from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from backend.core.config import settings

from backend.middleware.cors import add_cors_middleware
from backend.middleware.request_id import request_id_middleware
from backend.middleware.error_handler import global_exception_handler

from backend.api.health import router as health_router
from backend.api.upload import router as upload_router
from backend.api.stream import router as stream_router
from backend.api.predict import router as predict_router
from backend.api.xai import router as xai_router
from backend.api.report import router as report_router
from backend.api.rag import router as rag_router
from backend.api.similarity import router as similarity_router

from backend.middleware.audit_logging import audit_logging_middleware

app = FastAPI(title=settings.PROJECT_NAME)

# Fast API Middleware ordering: middleware is executed in the order it is added.
# Global exception handling
app.add_exception_handler(Exception, global_exception_handler)

# Request ID & Audit logging middleware
app.add_middleware(BaseHTTPMiddleware, dispatch=request_id_middleware)
app.add_middleware(BaseHTTPMiddleware, dispatch=audit_logging_middleware)

# CORS middleware is added at the outermost layer
add_cors_middleware(app)

# Register routers
app.include_router(health_router, prefix=settings.API_V1_STR, tags=["health"])
app.include_router(upload_router, prefix=f"{settings.API_V1_STR}/upload", tags=["upload"])
app.include_router(stream_router, prefix=f"{settings.API_V1_STR}/stream", tags=["stream"])
app.include_router(predict_router, prefix=f"{settings.API_V1_STR}/predict", tags=["predict"])
app.include_router(xai_router, prefix=f"{settings.API_V1_STR}/xai", tags=["xai"])
app.include_router(report_router, prefix=f"{settings.API_V1_STR}/report", tags=["report"])
app.include_router(rag_router, prefix=f"{settings.API_V1_STR}/rag", tags=["rag"])
app.include_router(similarity_router, prefix=f"{settings.API_V1_STR}/similarity", tags=["similarity"])

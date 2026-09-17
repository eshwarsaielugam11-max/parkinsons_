from starlette.requests import Request
from starlette.responses import Response
from backend.core.security import log_audit_event

async def audit_logging_middleware(request: Request, call_next):
    """
    Middleware that captures and logs clinical access to patient records,
    predictions, explainability reports, and upload endpoints.
    """
    client_ip = request.client.host if request.client else "127.0.0.1"
    path = request.url.path
    method = request.method

    response: Response = await call_next(request)

    # Intercept clinical paths
    if "/api/v1/" in path:
        action = None
        resource_type = None
        resource_id = "unknown"

        if "/predict/patients/" in path:
            action = "READ_PATIENT_HISTORY"
            resource_type = "patient_history"
            parts = path.split("/")
            if len(parts) >= 6:
                resource_id = parts[5]
        elif "/predict/" in path:
            action = "READ_PREDICTION_SESSION"
            resource_type = "session_prediction"
            resource_id = path.split("/")[-1]
        elif "/report/" in path:
            action = "GENERATE_OR_READ_REPORT"
            resource_type = "clinical_report"
            resource_id = path.split("/")[-1]
        elif "/xai/" in path:
            action = "READ_XAI_EVIDENCE"
            resource_type = "xai_evidence"
            resource_id = path.split("/")[-1]
        elif "/upload" in path and method == "POST":
            action = "CREATE_AUDIO_UPLOAD"
            resource_type = "audio_screening"
            resource_id = "upload_request"

        if action:
            log_audit_event(
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                actor="API_CLIENT",
                client_ip=client_ip,
                status="SUCCESS" if response.status_code < 400 else f"HTTP_{response.status_code}",
                details={"method": method, "path": path, "status_code": response.status_code}
            )

    return response

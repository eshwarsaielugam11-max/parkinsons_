import time
import uuid
import logging
from fastapi import Request
from starlette.responses import Response
from backend.core.logging import set_current_request_id, app_logger

async def request_id_middleware(request: Request, call_next):
    # Extract existing X-Request-ID or generate new UUID
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    set_current_request_id(request_id)
    request.state.request_id = request_id

    start_time = time.perf_counter()
    status_code = 500

    try:
        response: Response = await call_next(request)
        status_code = response.status_code
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        duration_ms = (time.perf_counter() - start_time) * 1000.0
        # Exclude high-frequency health checks from verbose logging to keep logs concise
        if request.url.path != "/api/v1/health":
            app_logger.info(
                f"HTTP {request.method} {request.url.path} -> {status_code} ({duration_ms:.1f}ms)",
                extra={
                    "structured_data": {
                        "event_type": "HTTP_REQUEST",
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": status_code,
                        "latency_ms": round(duration_ms, 2),
                        "client_ip": request.client.host if request.client else "unknown",
                    }
                }
            )
        # Clear context
        set_current_request_id(None)

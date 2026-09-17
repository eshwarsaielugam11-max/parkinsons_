import os
import re
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

# Configure specialized audit logger
audit_logger = logging.getLogger("pd_voice.audit")
if not audit_logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "event": "AUDIT_ACCESS", "message": %(message)s}'
    )
    handler.setFormatter(formatter)
    audit_logger.addHandler(handler)
    audit_logger.setLevel(logging.INFO)

# ===========================================================================
# 1. Prompt Injection Defense & Input Sanitization
# ===========================================================================

# Forbidden prompt override injection patterns
ADVERSARIAL_PROMPT_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+(instructions|prompts|rules)", re.IGNORECASE),
    re.compile(r"system\s*:", re.IGNORECASE),
    re.compile(r"\[/?(system|prompt|assistant|human|user|numeric_values|similarity_results)\]", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+(a|an|in|dan|unrestricted)", re.IGNORECASE),
    re.compile(r"disregard\s+(the\s+)?(above|rules|safety)", re.IGNORECASE),
    re.compile(r"<script.*?>.*?</script>", re.IGNORECASE),
]

def sanitize_user_text(text: Optional[str], max_length: int = 250) -> str:
    """
    Sanitize and constrain user-provided text inputs (e.g. patient ID, notes, metadata)
    to prevent prompt injection and delimiter tampering before reaching LLM or database.
    """
    if not text:
        return ""

    # Enforce strict length limits
    sanitized = text.strip()[:max_length]

    # Strip dangerous injection patterns
    for pattern in ADVERSARIAL_PROMPT_PATTERNS:
        sanitized = pattern.sub("[REDACTED_INJECTION_ATTEMPT]", sanitized)

    # Remove non-printable / control ASCII characters
    sanitized = "".join(ch for ch in sanitized if ch.isprintable() or ch in "\n\t")

    return sanitized


# ===========================================================================
# 2. Audio Retention Policy & Expired File Cleanup
# ===========================================================================

DEFAULT_AUDIO_RETENTION_DAYS = 30

def cleanup_expired_audio_files(
    storage_dir: str,
    retention_days: int = DEFAULT_AUDIO_RETENTION_DAYS,
    now: Optional[datetime] = None
) -> int:
    """
    Scans storage directory and deletes raw audio files (.wav, .mp3, .m4a)
    that exceed the retention window to comply with privacy minimization principles.
    Returns the count of deleted files.
    """
    if not os.path.exists(storage_dir):
        return 0

    current_time = now or datetime.now(timezone.utc)
    cutoff_time = current_time - timedelta(days=retention_days)
    cutoff_timestamp = cutoff_time.timestamp()

    deleted_count = 0

    for root, _, files in os.walk(storage_dir):
        for filename in files:
            if filename.lower().endswith(('.wav', '.mp3', '.m4a', '.mp4', '.tmp')):
                filepath = os.path.join(root, filename)
                try:
                    file_mtime = os.path.getmtime(filepath)
                    if file_mtime < cutoff_timestamp:
                        os.remove(filepath)
                        deleted_count += 1
                        log_audit_event(
                            action="AUDIO_RETENTION_PURGE",
                            resource_type="audio_file",
                            resource_id=filename,
                            actor="SYSTEM_CLEANUP_JOB",
                            status="DELETED",
                            details={"filepath": filepath, "mtime": file_mtime, "cutoff": cutoff_timestamp}
                        )
                except OSError as err:
                    logging.warning(f"Failed to remove expired audio file {filepath}: {err}")

    return deleted_count


# ===========================================================================
# 3. Clinical Audit Access Logger
# ===========================================================================

def log_audit_event(
    action: str,
    resource_type: str,
    resource_id: str,
    actor: str = "ANONYMOUS_CLIENT",
    client_ip: str = "127.0.0.1",
    status: str = "SUCCESS",
    details: Optional[Dict[str, Any]] = None
):
    """
    Records an immutable audit event for patient data access and PHI lifecycle.
    """
    import json
    payload = {
        "action": action,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "actor": actor,
        "client_ip": client_ip,
        "status": status,
        "details": details or {},
    }
    audit_logger.info(json.dumps(payload))

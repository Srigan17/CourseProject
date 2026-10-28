import json
import os
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pathlib import Path
from pydantic import BaseModel
from backend.app.config import settings

class AuditEvent(BaseModel):
    timestamp: str
    event_type: str  # e.g., AUTH_SUCCESS, AUTH_FAILURE, CLIENT_REGISTRATION, ROUND_START, ROUND_COMPLETE, SECAGG_SUCCESS, DP_CONFIG, UPDATE_REJECTED
    severity: str    # "INFO", "WARNING", "CRITICAL"
    actor: str       # username, client_id, or "SYSTEM"
    client_id: Optional[str] = None
    round_num: Optional[int] = None
    details: Dict[str, Any]
    security_verified: bool = True

class AuditLogger:
    def __init__(self, log_path: Path = settings.AUDIT_LOG_FILE):
        self.log_path = log_path
        self._in_memory_logs: List[Dict[str, Any]] = []
        self._load_existing_logs()

    def _load_existing_logs(self):
        if self.log_path.exists():
            try:
                with open(self.log_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            self._in_memory_logs.append(json.loads(line))
            except Exception:
                pass

    def log_event(
        self,
        event_type: str,
        severity: str,
        actor: str,
        details: Dict[str, Any],
        client_id: Optional[str] = None,
        round_num: Optional[int] = None,
        security_verified: bool = True
    ) -> Dict[str, Any]:
        """
        Appends an audit log event while redacting sensitive fields.
        """
        # Redact any accidental sensitive keys
        clean_details = {}
        forbidden_keys = {"password", "secret", "private_key", "raw_data", "plaintext_weights"}
        for k, v in details.items():
            if any(fk in k.lower() for fk in forbidden_keys):
                clean_details[k] = "[REDACTED_BY_SECURITY_POLICY]"
            else:
                clean_details[k] = v

        event = AuditEvent(
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type=event_type,
            severity=severity.upper(),
            actor=actor,
            client_id=client_id,
            round_num=round_num,
            details=clean_details,
            security_verified=security_verified
        ).model_dump()

        self._in_memory_logs.insert(0, event)  # newest first
        if len(self._in_memory_logs) > 5000:
            self._in_memory_logs = self._in_memory_logs[:5000]

        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(event) + "\n")
        except Exception:
            pass

        return event

    def get_logs(
        self,
        event_type: Optional[str] = None,
        severity: Optional[str] = None,
        client_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        filtered = self._in_memory_logs
        if event_type:
            filtered = [e for e in filtered if e["event_type"] == event_type]
        if severity:
            filtered = [e for e in filtered if e["severity"] == severity.upper()]
        if client_id:
            filtered = [e for e in filtered if e.get("client_id") == client_id]
        return filtered[:limit]

audit_logger = AuditLogger()

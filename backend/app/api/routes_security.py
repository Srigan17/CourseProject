import numpy as np
from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from backend.app.security.audit import audit_logger
from backend.app.security.crypto import cipher
from backend.app.security.certs import tls_manager
from backend.app.security.validation import validator

router = APIRouter(prefix="/security", tags=["Security & Audit"])

class AESPayload(BaseModel):
    plaintext: str = "Confidential Patient Vitals: HeartRate=78bpm, Activity=Running"
    associated_data: str = "hospital_a_ehrs"

@router.get("/audit-logs")
def get_audit_logs(
    event_type: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    client_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500)
) -> List[Dict[str, Any]]:
    return audit_logger.get_logs(
        event_type=event_type,
        severity=severity,
        client_id=client_id,
        limit=limit
    )

@router.get("/tls-status")
def get_tls_status() -> Dict[str, Any]:
    return tls_manager.get_status()

@router.post("/crypto/aes-gcm/test")
def test_aes_gcm(payload: AESPayload) -> Dict[str, Any]:
    enc = cipher.encrypt(payload.plaintext, associated_data=payload.associated_data)
    decrypted = cipher.decrypt(enc["ciphertext"], enc["nonce"], associated_data=payload.associated_data)
    return {
        "original_plaintext": payload.plaintext,
        "encrypted_result": enc,
        "decrypted_plaintext": decrypted,
        "verified": bool(payload.plaintext == decrypted),
        "algorithm": "AES-256-GCM (Authenticated Encryption with 96-bit Nonce)"
    }

@router.post("/validation/test-anomaly-detection")
def test_anomaly_detection() -> Dict[str, Any]:
    """
    Demonstrates model update validation and Krum outlier rejection
    against simulated poisoning attacks.
    """
    np.random.seed(42)
    # 3 legitimate updates
    legit_1 = np.random.normal(0.0, 0.1, size=20)
    legit_2 = np.random.normal(0.0, 0.1, size=20)
    legit_3 = np.random.normal(0.0, 0.1, size=20)
    # 1 poisoned Byzantine update
    poisoned = np.random.normal(15.0, 2.0, size=20)

    client_ids = ["hospital_a", "hospital_b", "hospital_c", "malicious_client_x"]
    updates = [legit_1, legit_2, legit_3, poisoned]

    krum_res = validator.detect_outliers_krum(updates, client_ids)

    return {
        "clients_evaluated": client_ids,
        "krum_outlier_detection": krum_res,
        "attack_prevented": "malicious_client_x" in krum_res["rejected_clients"],
        "defense_algorithm": "Krum Euclidean Distance Outlier Defense"
    }

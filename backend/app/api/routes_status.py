from fastapi import APIRouter
from typing import Dict, Any
from backend.app.config import settings
from backend.app.ml.datasets import dataset_manager

router = APIRouter(tags=["System Status"])

@router.get("/status")
def get_system_status() -> Dict[str, Any]:
    datasets = dataset_manager.list_all_datasets()
    available_count = sum(1 for d in datasets if d["is_available"])
    return {
        "project_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "backend": "FastAPI (Python 3.14)",
        "security_services": {
            "jwt_auth": "Active (HS256)",
            "aes_gcm": "Active (AES-256-GCM)",
            "tls_mtls": "Configured (TLS 1.3)",
            "audit_logging": "Active (Structured JSONL)",
            "update_validator": "Active (Outlier & Byzantine Check)"
        },
        "privacy_services": {
            "differential_privacy": "Gaussian / Laplace with Analytical Composition",
            "secure_aggregation": "Paillier Additive Homomorphic Cryptosystem"
        },
        "fhir_interoperability": "HL7 FHIR R4 (Patient, Observation, Device)",
        "datasets": {
            "total": len(datasets),
            "available": available_count,
            "items": [{"id": d["id"], "name": d["name"], "status": d["status"]} for d in datasets]
        }
    }

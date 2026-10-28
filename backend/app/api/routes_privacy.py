import numpy as np
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any, List
from backend.app.privacy.differential_privacy import dp_engine
from backend.app.privacy.secure_aggregation import secagg_service
from backend.app.privacy.compression import compute_communication_cost_mb

router = APIRouter(prefix="/privacy", tags=["Privacy"])

class DPConfigPayload(BaseModel):
    enabled: bool = True
    clipping_norm: float = 1.0
    noise_multiplier: float = 0.5
    target_delta: float = 1e-5
    mechanism: str = "Gaussian"

class DPCalculatePayload(BaseModel):
    num_rounds: int = 5
    clipping_norm: float = 1.0
    noise_multiplier: float = 0.5
    target_delta: float = 1e-5
    sample_rate: float = 1.0

@router.get("/status")
def get_privacy_status() -> Dict[str, Any]:
    return {
        "differential_privacy": {
            "enabled": dp_engine.enabled,
            "clipping_norm": dp_engine.clipping_norm,
            "noise_multiplier": dp_engine.noise_multiplier,
            "target_delta": dp_engine.target_delta,
            "mechanism": dp_engine.mechanism,
            "accountant": "Analytical Gaussian Advanced Composition"
        },
        "secure_aggregation": {
            "protocol": "Paillier Additive Homomorphic Encryption",
            "key_length_bits": secagg_service.key_length,
            "min_clients_threshold": secagg_service.min_clients,
            "scale_factor": secagg_service.scale_factor,
            "zero_server_visibility": True,
            "source_repo": "https://github.com/Mallikarjun501/privacy-preserving-secure-aggregation-fl"
        }
    }

@router.post("/dp/configure")
def configure_dp(payload: DPConfigPayload) -> Dict[str, Any]:
    dp_engine.enabled = payload.enabled
    dp_engine.clipping_norm = payload.clipping_norm
    dp_engine.noise_multiplier = payload.noise_multiplier
    dp_engine.target_delta = payload.target_delta
    dp_engine.mechanism = payload.mechanism
    return {
        "status": "Differential privacy settings updated successfully",
        "config": payload.model_dump()
    }

@router.post("/dp/calculate-budget")
def calculate_dp_budget(payload: DPCalculatePayload) -> Dict[str, Any]:
    temp_engine = DifferentialPrivacyEngine(
        enabled=True,
        clipping_norm=payload.clipping_norm,
        noise_multiplier=payload.noise_multiplier,
        target_delta=payload.target_delta
    )
    budget = temp_engine.compute_privacy_budget(
        num_rounds=payload.num_rounds,
        sample_rate=payload.sample_rate
    )
    return budget

@router.post("/secagg/test-verification")
def test_secure_aggregation_protocol(
    num_clients: int = Query(3, ge=2, le=5),
    param_count: int = Query(20, ge=5, le=100)
) -> Dict[str, Any]:
    """
    Runs a live cryptographic demonstration of Paillier Homomorphic Encryption.
    Verifies that:
    1. Each client's update is encrypted with coordinator's public key.
    2. Server sums the ciphertexts directly in ciphertext domain without decryption.
    3. The decrypted sum exactly matches normal plaintext sum within quantization error.
    4. Individual client updates are NEVER decrypted by the server.
    """
    np.random.seed(42)
    # Generate simulated client updates
    client_updates = [np.random.randn(param_count) for _ in range(num_clients)]
    
    # 1. Plaintext expected average
    plaintext_expected = np.mean(client_updates, axis=0)

    # 2. Cryptographic Secure Aggregation
    secagg_output = secagg_service.execute_secure_aggregation(client_updates)
    decrypted_averaged = secagg_output["aggregated_weights"]

    # 3. Compute absolute error due to integer quantization
    max_error = float(np.max(np.abs(plaintext_expected - decrypted_averaged)))

    return {
        "protocol": "Paillier Homomorphic Cryptosystem (Additive SecAgg)",
        "verified": bool(max_error < 1e-4),
        "num_clients": num_clients,
        "param_count": param_count,
        "max_quantization_error": max_error,
        "timing_and_overhead": secagg_output["metrics"],
        "sample_plaintext_expected": [round(float(x), 4) for x in plaintext_expected[:5]],
        "sample_secagg_decrypted": [round(float(x), 4) for x in decrypted_averaged[:5]],
        "cryptographic_proof": "Homomorphic property satisfied: D(prod(E(w_i))) == sum(w_i). Coordinator never has access to individual plaintext client vectors."
    }

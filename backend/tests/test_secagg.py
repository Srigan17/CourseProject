import numpy as np
import pytest
from backend.app.privacy.secure_aggregation import PaillierSecureAggregationService

def test_paillier_homomorphic_secure_aggregation_signed_floats():
    service = PaillierSecureAggregationService(key_length=512, min_clients=3)
    
    # 3 simulated hospital clients with positive, negative, and small weight updates
    w1 = np.array([0.523456, -0.218934, 1.412890, -0.054321])
    w2 = np.array([0.112233,  0.887766, -0.334455, 0.254321])
    w3 = np.array([-0.254321, 0.445566, 0.778899, -0.109876])
    
    expected_mean = np.mean([w1, w2, w3], axis=0)

    # Execute secure aggregation
    result = service.execute_secure_aggregation([w1, w2, w3])
    aggregated = result["aggregated_weights"]

    # Verify numerical precision within quantization scale factor (1e6)
    np.testing.assert_allclose(aggregated, expected_mean, atol=1e-4)

    # Verify protocol semantics: zero plaintext visibility, NOT zero-knowledge proof
    assert result["metrics"]["zero_server_plaintext_visibility"] is True
    assert result["metrics"]["num_clients"] == 3
    assert "PROTOTYPE KEY LENGTH" in result["metrics"]["security_advisory"]

def test_threshold_enforcement():
    service = PaillierSecureAggregationService(key_length=512, min_clients=3)
    # Only 2 clients submitted updates, below threshold of 3
    w1 = np.array([0.5, 0.2])
    w2 = np.array([0.1, 0.8])
    with pytest.raises(ValueError, match="Need at least 3 clients"):
        service.execute_secure_aggregation([w1, w2])

def test_dimension_mismatch_rejection():
    service = PaillierSecureAggregationService(key_length=512, min_clients=2)
    # Client 1 sends 3 params, Client 2 sends 4 params
    w1 = np.array([0.1, 0.2, 0.3])
    w2 = np.array([0.1, 0.2, 0.3, 0.4])
    enc1 = service.encrypt_client_update(w1)
    enc2 = service.encrypt_client_update(w2)
    with pytest.raises(ValueError, match="parameter dimension mismatch"):
        service.aggregate_ciphertexts([enc1, enc2])

def test_extreme_values_and_overflow_handling():
    service = PaillierSecureAggregationService(key_length=512, min_clients=2)
    # Test extreme values
    w1 = np.array([1e3, -1e3, 0.0, 1e-4])
    w2 = np.array([-1e3, 1e3, 0.0, -1e-4])
    result = service.execute_secure_aggregation([w1, w2])
    aggregated = result["aggregated_weights"]
    expected = np.array([0.0, 0.0, 0.0, 0.0])
    np.testing.assert_allclose(aggregated, expected, atol=1e-3)

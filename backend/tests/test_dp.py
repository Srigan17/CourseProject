import numpy as np
from backend.app.privacy.differential_privacy import DifferentialPrivacyEngine

def test_l2_norm_clipping():
    dp = DifferentialPrivacyEngine(enabled=True, clipping_norm=1.0)
    large_weights = np.array([2.0, 2.0, 2.0, 2.0])  # norm = 4.0
    clipped, norm = dp.clip_update(large_weights)
    new_norm = np.linalg.norm(clipped)
    assert np.isclose(new_norm, 1.0, atol=1e-5)

def test_dp_noise_addition():
    dp = DifferentialPrivacyEngine(enabled=True, clipping_norm=1.0, noise_multiplier=0.5)
    weights = np.array([0.1, 0.2, 0.3])
    noisy_weights = dp.add_noise(weights)
    assert not np.array_equal(weights, noisy_weights)
    assert noisy_weights.shape == weights.shape

def test_privacy_accountant_calculation():
    dp = DifferentialPrivacyEngine(enabled=True, clipping_norm=1.0, noise_multiplier=0.8, target_delta=1e-5)
    budget = dp.compute_privacy_budget(num_rounds=5)
    assert budget["is_private"] is True
    assert budget["epsilon"] > 0
    assert budget["delta"] == 1e-5
    assert budget["epsilon"] < float("inf")

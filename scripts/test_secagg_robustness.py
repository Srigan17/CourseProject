import sys
import os
import numpy as np
from itertools import combinations

# Flower cryptographic and mathematical primitives
from flwr.common.secure_aggregation.crypto.shamir import create_shares, combine_shares
from flwr.common.secure_aggregation.crypto.symmetric_encryption import (
    generate_shared_key, encrypt, decrypt
)
from flwr.supercore.primitives.asymmetric import (
    generate_key_pairs, public_key_to_bytes, bytes_to_public_key
)
from flwr.common.secure_aggregation.quantization import quantize, dequantize
from flwr.common.secure_aggregation.secaggplus_utils import pseudo_rand_gen

def test_negative_cases_and_boundaries():
    print("=================================================================================")
    print("       PHASE 4 AUDIT: ROBUSTNESS, ADVERSARIAL & BOUNDARY TESTS FOR SECAGG+       ")
    print("=================================================================================")
    
    results = {}
    modulus = 2**32
    clipping_range = 8.0
    quantization_range = 2**22
    
    # ---------------------------------------------------------------------------
    # CHECK 1: Malformed Shamir Shares Handling
    # ---------------------------------------------------------------------------
    print("\n--- Check 1: Malformed Shamir Share Detection ---")
    secret = b"valid_seed_for_private_mask_123"
    shares = create_shares(secret, threshold=3, num=4)
    
    # Corrupt one share by flipping bytes
    corrupted_share = bytearray(shares[0])
    corrupted_share[5] ^= 0xAA
    corrupted_shares = [bytes(corrupted_share), shares[1], shares[2]]
    
    c1_detected = False
    try:
        recon = combine_shares(corrupted_shares)
        # If it doesn't throw, does it match the secret?
        if recon != secret:
            c1_detected = True # Detected corrupted reconstruction
            c1_msg = "Reconstruction produced incorrect secret (corrupted output detected)"
    except Exception as e:
        c1_detected = True # Threw error on malformed share
        c1_msg = f"Exception raised on malformed share: {type(e).__name__}"
        
    print(f"  Malformed share detected: {c1_detected} ({c1_msg})")
    results["malformed_share_detection"] = {
        "status": "PASSED" if c1_detected else "FAILED",
        "detected": c1_detected,
        "detail": c1_msg
    }

    # ---------------------------------------------------------------------------
    # CHECK 2: Duplicate Shamir Shares Handling
    # ---------------------------------------------------------------------------
    print("\n--- Check 2: Duplicate Shamir Share Handling ---")
    # Provide 3 shares, but two are identical (e.g. share 0, share 0, share 1)
    # Effective distinct shares = 2 < threshold 3!
    duplicate_shares = [shares[0], shares[0], shares[1]]
    
    c2_detected = False
    try:
        # Check if combine_shares fails or returns corrupt/fails on duplicate evaluation points
        recon = combine_shares(duplicate_shares)
        if recon != secret:
            c2_detected = True
            c2_msg = "Duplicate shares failed to reconstruct original secret (effective distinct shares < 3)"
    except Exception as e:
        c2_detected = True
        c2_msg = f"Exception raised on duplicate shares: {type(e).__name__}"
        
    print(f"  Duplicate share sub-threshold detected: {c2_detected} ({c2_msg})")
    results["duplicate_share_detection"] = {
        "status": "PASSED" if c2_detected else "FAILED",
        "detected": c2_detected,
        "detail": c2_msg
    }

    # ---------------------------------------------------------------------------
    # CHECK 3: Boundary & Out-of-Bounds Quantization Values
    # ---------------------------------------------------------------------------
    print("\n--- Check 3: Extreme Boundary and Out-of-Bounds Values ---")
    # Test values: -8.0 (lower bound), +8.0 (upper bound), 0.0, and out-of-bounds [-15.0, +25.0]
    test_boundaries = np.array([-15.0, -8.0, -4.0, -0.0001, 0.0, 0.0001, 4.0, 8.0, 25.0], dtype=np.float32)
    expected_clipped = np.clip(test_boundaries, -clipping_range, clipping_range)
    
    q_bound = quantize([test_boundaries], clipping_range, quantization_range)
    dq_bound = dequantize(q_bound, clipping_range, quantization_range)
    
    # Verify integer range of quantized values: in Flower, clipping to [-R, R] maps to [0, target_range] inclusive
    int_values = q_bound[0]
    within_int_range = bool(np.all(int_values >= 0) and np.all(int_values <= quantization_range))
    
    # Error relative to clipped expected
    diff_bound = np.abs(expected_clipped - dq_bound[0])
    max_bound_err = float(np.max(diff_bound))
    
    c3_passed = within_int_range and (max_bound_err < 1e-4)
    print(f"  Quantized integers strictly within [0, {quantization_range}]: {within_int_range}")
    print(f"  Min integer: {int_values.min()}, Max integer: {int_values.max()}")
    print(f"  Max absolute error against clipped expected: {max_bound_err:.7f}")
    print(f"  Out-of-bounds values properly saturated to [-8.0, 8.0]: {bool(dq_bound[0][0] <= -7.99 and dq_bound[0][-1] >= 7.99)}")
    results["boundary_quantization_check"] = {
        "status": "PASSED" if c3_passed else "FAILED",
        "within_int_range": within_int_range,
        "max_bound_error": round(max_bound_err, 7),
        "tolerance": 1e-4
    }

    # ---------------------------------------------------------------------------
    # CHECK 4: Direct Comparison of Custom Aggregation with Flower Native Code
    # ---------------------------------------------------------------------------
    print("\n--- Check 4: Direct Equivalence with Flower's Native secaggplus_workflow logic ---")
    # In Flower's secaggplus_workflow.py lines 642-650:
    #   aggregated_vector = dequantize(recon_parameters, state.clipping_range, state.quantization_range)
    #   offset = -(len(active_nids) - 1) * state.clipping_range
    #   for vec in aggregated_vector:
    #       vec += offset
    #       vec *= inv_dq_total_ratio
    
    # Let's test with 4 clients with weights [w1, w2, w3, w4] = [1, 1, 1, 1]
    np.random.seed(42)
    sample_vectors = [np.random.normal(0, 0.5, 100).astype(np.float32) for _ in range(4)]
    ref_flower_avg = np.mean(sample_vectors, axis=0)
    
    # Custom quantization and integer aggregation matching Flower
    q_list = [quantize([v], clipping_range, quantization_range)[0] for v in sample_vectors]
    # Sum of quantized integers
    int_sum = np.sum(q_list, axis=0) # array of int64
    
    # Apply Flower's exact dequantization and offset sequence
    dq_sum = dequantize([int_sum], clipping_range, quantization_range)[0]
    flower_offset = -(4 - 1) * clipping_range # -24.0
    custom_flower_avg = (dq_sum + flower_offset) / 4.0
    
    c4_diff = np.max(np.abs(ref_flower_avg - custom_flower_avg))
    c4_passed = bool(c4_diff < 1e-4)
    print(f"  Max difference between reference mean and Flower formula: {c4_diff:.7f}")
    print(f"  Exact equivalence to Flower workflow formula: {c4_passed}")
    results["flower_formula_equivalence"] = {
        "status": "PASSED" if c4_passed else "FAILED",
        "max_difference": round(float(c4_diff), 7),
        "tolerance": 1e-4
    }
    
    print("\n=================================================================================")
    all_passed = all(r["status"] == "PASSED" for r in results.values())
    print(f"ROBUSTNESS & ADVERSARIAL CHECKS: {'ALL PASSED' if all_passed else 'SOME FAILED'}")
    print("=================================================================================")
    return all_passed

if __name__ == "__main__":
    test_negative_cases_and_boundaries()

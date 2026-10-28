import time
import numpy as np
from flwr.common.secure_aggregation.crypto.shamir import create_shares, combine_shares
from flwr.common.secure_aggregation.crypto.symmetric_encryption import generate_shared_key
from flwr.supercore.primitives.asymmetric import generate_key_pairs
from flwr.common.secure_aggregation.quantization import quantize, dequantize
from flwr.common.secure_aggregation.secaggplus_utils import pseudo_rand_gen

def run_live_crypto_benchmark(k=4, threshold=3):
    """
    Executes actual Flower 1.42 cryptographic primitives and measures real microsecond latencies.
    """
    shapes = [(128, 16), (128,), (64, 128), (64,), (32, 64), (32,), (6, 32), (6,)]
    modulus = 2**31 - 1
    clipping_range = 8.0
    quantization_range = 2**16
    
    # 1. Asymmetric Key Generation (X25519)
    t0 = time.perf_counter()
    client_keys = [generate_key_pairs() for _ in range(k)]
    t_keygen = (time.perf_counter() - t0) * 1000.0 / k # per client
    
    # 2. Diffie-Hellman Key Agreement
    t0 = time.perf_counter()
    s_uv = generate_shared_key(client_keys[0][0], client_keys[1][1])
    t_dh = (time.perf_counter() - t0) * 1000.0
    
    # 3. Shamir Secret Sharing (t=3, n=4)
    b_seed = b"healthfl_secagg_seed_32bytes_123"
    t0 = time.perf_counter()
    shares = create_shares(b_seed, threshold=threshold, num=k)
    t_shamir_create = (time.perf_counter() - t0) * 1000.0
    
    # 4. Shamir Reconstruction
    t0 = time.perf_counter()
    recovered = combine_shares(shares[:threshold])
    t_shamir_recon = (time.perf_counter() - t0) * 1000.0
    assert recovered == b_seed, "Reconstructed secret mismatch!"
    
    # 5. Stochastic/Uniform Quantization
    dummy_params = [np.random.randn(*s).astype(np.float32) * 0.1 for s in shapes]
    t0 = time.perf_counter()
    q_params = quantize(dummy_params, clipping_range, quantization_range)
    t_quant = (time.perf_counter() - t0) * 1000.0
    
    # 6. Pseudo-Random Generator (PRG) Masking
    seed_32 = b"healthfl_prg_mask_seed_32bytes!!" # exactly 32 bytes (32 & 0x3 == 0)
    t0 = time.perf_counter()
    m_list = pseudo_rand_gen(seed_32, modulus, shapes)
    t_prg = (time.perf_counter() - t0) * 1000.0
    
    # 7. Modulo Arithmetic & Server Mask Cancellation
    t0 = time.perf_counter()
    masked_sum = [np.zeros(s, dtype=np.int64) for s in shapes]
    for idx in range(len(shapes)):
        # Simulate summing 4 masked client tensors
        masked_sum[idx] = (q_params[idx].astype(np.int64) + m_list[idx]) % modulus
        # Subtract PRG mask
        unmasked = (masked_sum[idx] - m_list[idx]) % modulus
    t_unmask = (time.perf_counter() - t0) * 1000.0
    
    # 8. Dequantization
    t0 = time.perf_counter()
    dequantized = dequantize([unmasked.astype(np.int64) for _ in shapes], clipping_range, quantization_range)
    t_dequant = (time.perf_counter() - t0) * 1000.0
    
    total_client_latency = t_keygen + (k - 1) * t_dh + t_shamir_create + t_quant + t_prg
    total_server_latency = (k - threshold) * t_shamir_recon + t_unmask + t_dequant
    
    return {
        "client_keygen_ms": round(t_keygen, 3),
        "diffie_hellman_ms": round(t_dh, 3),
        "shamir_create_ms": round(t_shamir_create, 3),
        "shamir_reconstruct_ms": round(t_shamir_recon, 3),
        "quantization_ms": round(t_quant, 3),
        "prg_expansion_ms": round(t_prg, 3),
        "server_unmasking_ms": round(t_unmask, 3),
        "dequantization_ms": round(t_dequant, 3),
        "total_client_crypto_overhead_ms": round(total_client_latency, 2),
        "total_server_crypto_overhead_ms": round(total_server_latency, 2),
        "total_round_crypto_overhead_ms": round(total_client_latency + total_server_latency, 2),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

if __name__ == "__main__":
    res = run_live_crypto_benchmark()
    print("Live Crypto Benchmark Result:", res)

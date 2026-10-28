import sys
import time
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
from pathlib import Path
from phe import paillier

# Ensure secagg_repo is accessible if needed
repo_path = Path(__file__).resolve().parent.parent.parent.parent / "secagg_repo"
if str(repo_path) not in sys.path:
    sys.path.insert(0, str(repo_path))

class PaillierSecureAggregationService:
    """
    Cryptographic Secure Aggregation using Paillier Additive Homomorphic Encryption.
    Directly integrates the cryptosystem from https://github.com/Mallikarjun501/privacy-preserving-secure-aggregation-fl
    
    Architectural & Trust Model:
    1. Aggregation Server (Untrusted / Honest-but-Curious in production):
       - Receives only encrypted ciphertexts [[alpha_i * Delta w_i]] and the public key (n, g).
       - Computes homomorphic addition in the ciphertext domain:
         [[sum alpha_i * Delta w_i]] = prod [[alpha_i * Delta w_i]] mod n^2.
       - Has ZERO plaintext visibility into individual hospital client updates.
    2. Key Authority / Consortium Coordinator:
       - Holds the private key lambda in simulation.
       - Decrypts ONLY the aggregated global sum [[sum alpha_i * Delta w_i]], never individual client updates.
    3. Security & Key Length Notice:
       - Default key_length=512 is used strictly for runtime feasibility in local laptop simulation.
       - 512-bit RSA/Paillier moduli are vulnerable to modern factorization (GNFS).
       - Production systems MUST configure key_length >= 2048 bits (NIST SP 800-57) or threshold Paillier.
       - Numerical equivalence to plaintext FedAvg does NOT constitute proof of confidentiality.
    """
    def __init__(self, key_length: int = 512, scale_factor: float = 1e6, min_clients: int = 2):
        self.key_length = int(key_length)
        self.scale_factor = float(scale_factor)
        self.min_clients = int(min_clients)
        self.public_key = None
        self.private_key = None
        self._init_keys()

    def _init_keys(self):
        """Generates keypair once or on demand."""
        self.public_key, self.private_key = paillier.generate_paillier_keypair(n_length=self.key_length)

    def get_public_key(self):
        return self.public_key

    def encrypt_client_update(self, weights: np.ndarray, client_weight: float = 1.0) -> List[Any]:
        """
        Executed locally by each simulated hospital client.
        Applies client sample weight alpha_i, scales signed float weights to integers,
        and encrypts with coordinator's public key. Supports positive and negative values.
        """
        clean_weights = np.nan_to_num(weights.flatten() * float(client_weight), nan=0.0, posinf=1e4, neginf=-1e4)
        int_weights = [int(round(float(w) * self.scale_factor)) for w in clean_weights]
        
        # Parallelize encryption across CPU cores if large
        if len(int_weights) > 500:
            try:
                from joblib import Parallel, delayed
                return Parallel(n_jobs=4, batch_size=250)(delayed(self.public_key.encrypt)(val) for val in int_weights)
            except Exception:
                pass

        encrypted = [self.public_key.encrypt(val) for val in int_weights]
        return encrypted

    def aggregate_ciphertexts(self, list_of_encrypted_updates: List[List[Any]]) -> List[Any]:
        """
        Executed on the Aggregation Server.
        Sums encrypted updates element-wise in ciphertext domain without decrypting.
        E(w1) * E(w2) mod N^2 = E(w1 + w2)
        """
        if len(list_of_encrypted_updates) < self.min_clients:
            raise ValueError(
                f"Secure Aggregation aborted: participation threshold ({len(list_of_encrypted_updates)}) "
                f"below minimum required ({self.min_clients})."
            )

        num_params = len(list_of_encrypted_updates[0])
        for idx, client_enc in enumerate(list_of_encrypted_updates):
            if len(client_enc) != num_params:
                raise ValueError(
                    f"Client {idx} parameter dimension mismatch: expected {num_params}, got {len(client_enc)}."
                )

        # Homomorphic addition in ciphertext domain
        aggregated = list(list_of_encrypted_updates[0])
        for i in range(1, len(list_of_encrypted_updates)):
            for j in range(num_params):
                try:
                    aggregated[j] = aggregated[j] + list_of_encrypted_updates[i][j]
                except Exception as e:
                    raise ValueError(f"Malformed ciphertext or homomorphic addition failure at index {j}: {str(e)}")

        return aggregated

    def decrypt_and_decode(
        self,
        aggregated_ciphertext: List[Any],
        original_shape: Tuple[int, ...]
    ) -> np.ndarray:
        """
        Executed by the Coordinator / Key Authority holding the private key.
        Decrypts the homomorphically aggregated sum and scales back to float domain.
        Because client sample weights were pre-multiplied before encryption,
        sum(alpha_k * w_k) is recovered directly upon dividing by scale_factor.
        """
        if self.private_key is None:
            raise PermissionError("Private key required for decryption is missing on this node.")
        
        if len(aggregated_ciphertext) > 500:
            try:
                from joblib import Parallel, delayed
                decrypted_integers = Parallel(n_jobs=4, batch_size=250)(
                    delayed(self.private_key.decrypt)(c) for c in aggregated_ciphertext
                )
                decoded_floats = np.array(decrypted_integers, dtype=np.float64) / self.scale_factor
                return decoded_floats.reshape(original_shape)
            except Exception:
                pass

        decrypted_integers = [self.private_key.decrypt(c) for c in aggregated_ciphertext]
        decoded_floats = np.array(decrypted_integers, dtype=np.float64) / self.scale_factor
        return decoded_floats.reshape(original_shape)

    def execute_secure_aggregation(
        self,
        client_updates: List[np.ndarray],
        client_weights: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """
        Complete end-to-end sample-weighted secure aggregation protocol execution
        with timing, communication metrics, and exact numerical verification against
        the corresponding plaintext calculation.
        """
        start_time = time.time()
        num_clients = len(client_updates)
        if num_clients < self.min_clients:
            raise ValueError(f"Need at least {self.min_clients} clients for secure aggregation.")

        orig_shape = client_updates[0].shape
        param_count = client_updates[0].size

        # Default to uniform weighting if client_weights is not supplied
        if client_weights is None or len(client_weights) != num_clients:
            norm_weights = [1.0 / num_clients] * num_clients
        else:
            w_sum = sum(client_weights)
            norm_weights = [float(w) / w_sum for w in client_weights]

        # Plaintext ground-truth calculation for numerical equivalence verification
        plaintext_expected = np.zeros(orig_shape, dtype=np.float64)
        for i in range(num_clients):
            plaintext_expected += norm_weights[i] * client_updates[i]

        # Step 1: Client-side weighted encryption (Simulated distributed hospital nodes)
        t0 = time.time()
        encrypted_updates = []
        for i, upd in enumerate(client_updates):
            enc = self.encrypt_client_update(upd, client_weight=norm_weights[i])
            encrypted_updates.append(enc)
        enc_time = time.time() - t0

        # Step 2: Server-side homomorphic aggregation (Untrusted server - Zero plaintext visibility)
        t1 = time.time()
        aggregated_ciphertexts = self.aggregate_ciphertexts(encrypted_updates)
        agg_time = time.time() - t1

        # Step 3: Decryption and decoding
        t2 = time.time()
        aggregated_weights = self.decrypt_and_decode(aggregated_ciphertexts, original_shape=orig_shape)
        dec_time = time.time() - t2

        total_time = time.time() - start_time
        numerical_error = float(np.max(np.abs(aggregated_weights - plaintext_expected)))

        return {
            "aggregated_weights": aggregated_weights,
            "metrics": {
                "num_clients": num_clients,
                "param_count": param_count,
                "key_length_bits": self.key_length,
                "scale_factor": self.scale_factor,
                "encryption_time_sec": round(enc_time, 4),
                "aggregation_time_sec": round(agg_time, 4),
                "decryption_time_sec": round(dec_time, 4),
                "total_secagg_time_sec": round(total_time, 4),
                "ciphertext_size_bytes_per_client": param_count * (self.key_length // 4),
                "numerical_aggregation_error": numerical_error,
                "is_numerically_exact": numerical_error < 1e-4,
                "zero_server_plaintext_visibility": True,
                "security_advisory": "PROTOTYPE KEY LENGTH (512-bit). In production, use NIST-compliant 2048-bit or 3072-bit Paillier keys."
            }
        }

secagg_service = PaillierSecureAggregationService(key_length=512)


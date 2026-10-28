import numpy as np
from typing import List, Tuple, Dict, Any

class ModelUpdateValidator:
    """
    Validates model updates sent from clients before aggregation.
    Guards against NaN/Inf values, shape mismatches, and malicious weight poisoning.
    """
    def __init__(self, expected_dim: int = None, max_norm: float = 500.0):
        self.expected_dim = expected_dim
        self.max_norm = max_norm

    def validate_single_update(self, weights: np.ndarray, client_id: str) -> Tuple[bool, str]:
        if not isinstance(weights, np.ndarray):
            return False, f"Client {client_id}: weights must be a numpy ndarray."
        
        if np.isnan(weights).any():
            return False, f"Client {client_id}: weights contain NaN values."
            
        if np.isinf(weights).any():
            return False, f"Client {client_id}: weights contain Infinite values."
            
        if self.expected_dim is not None and weights.size != self.expected_dim:
            return False, f"Client {client_id}: parameter count mismatch (expected {self.expected_dim}, got {weights.size})."
            
        l2_norm = float(np.linalg.norm(weights))
        if l2_norm > self.max_norm:
            return False, f"Client {client_id}: update L2 norm ({l2_norm:.2f}) exceeds maximum allowable threshold ({self.max_norm:.2f}). Possible poisoning."
            
        return True, "Valid"

    def detect_outliers_krum(self, updates: List[np.ndarray], client_ids: List[str], num_byzantine: int = 1) -> Dict[str, Any]:
        """
        Uses pairwise Euclidean distance matrix to score updates and identify outliers
        (based on the Byzantine resilience mechanism in the research repo).
        """
        n = len(updates)
        if n < 3:
            return {"accepted_clients": client_ids, "rejected_clients": [], "scores": {cid: 0.0 for cid in client_ids}}

        scores = {}
        for i in range(n):
            distances = []
            for j in range(n):
                if i != j:
                    d_sq = float(np.sum(np.square(updates[i] - updates[j])))
                    distances.append(d_sq)
            distances.sort()
            # Krum considers n - f - 2 closest neighbors
            k = max(1, n - num_byzantine - 2)
            scores[client_ids[i]] = sum(distances[:k])

        # Outlier is anyone whose distance is substantially higher than the median
        median_score = float(np.median(list(scores.values())))
        threshold = max(median_score * 3.0, 1.0)
        
        accepted = []
        rejected = []
        for cid, sc in scores.items():
            if sc > threshold:
                rejected.append(cid)
            else:
                accepted.append(cid)
                
        return {
            "accepted_clients": accepted,
            "rejected_clients": rejected,
            "scores": scores,
            "threshold": threshold
        }

validator = ModelUpdateValidator()

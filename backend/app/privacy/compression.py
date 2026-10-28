import numpy as np

def adaptive_quantization(weights: np.ndarray, bit_precision: int = 8) -> np.ndarray:
    """
    Applies adaptive quantization to weights (from research repo Eq. 7):
    Q(w) = floor(w * 2^b) / 2^b
    """
    scale = 2 ** bit_precision
    return np.floor(weights * scale) / scale

def sparse_gradient_sharing(weights: np.ndarray, threshold: float = 0.01) -> np.ndarray:
    """
    Zeros out small gradient weights below threshold (from research repo Eq. 8):
    S(w) = { w_j | |w_j| > tau }
    """
    sparse_weights = np.copy(weights)
    sparse_weights[np.abs(sparse_weights) < threshold] = 0.0
    return sparse_weights

def compute_communication_cost_mb(weights: np.ndarray, mode: str = "uncompressed") -> float:
    if mode == "uncompressed":
        return (weights.size * 4) / 1e6
    elif mode == "quantized_8bit":
        return weights.size / 1e6
    elif mode == "sparse_top10":
        non_zeros = np.count_nonzero(weights)
        return (non_zeros * 4) / 1e6
    return (weights.size * 4) / 1e6

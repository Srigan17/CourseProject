import numpy as np
from typing import List

def krum_filter(updates: List[np.ndarray]) -> np.ndarray:
    """
    Implements the Krum filter for Byzantine resilience from the provided research repo.
    Selects the single most representative update from a list.
    score_i = sum_{j != i} ||w_i - w_j||^2
    w^{t+1} = argmin_{w_i} score_i
    """
    if not updates:
        raise ValueError("Update list cannot be empty.")
    num_updates = len(updates)
    if num_updates == 1:
        return updates[0]

    scores = []
    for i in range(num_updates):
        score = 0.0
        for j in range(num_updates):
            if i == j:
                continue
            distance_sq = float(np.sum(np.square(updates[i] - updates[j])))
            score += distance_sq
        scores.append(score)

    min_score_index = int(np.argmin(scores))
    return updates[min_score_index]

def multi_krum(updates: List[np.ndarray], m: int = 2) -> np.ndarray:
    """
    Multi-Krum selects top m candidates and averages them.
    """
    if len(updates) <= m:
        return np.mean(updates, axis=0)
    scores = []
    for i in range(len(updates)):
        dists = [float(np.sum(np.square(updates[i] - updates[j]))) for j in range(len(updates)) if i != j]
        scores.append(sum(dists))
    top_indices = np.argsort(scores)[:m]
    selected = [updates[idx] for idx in top_indices]
    return np.mean(selected, axis=0)

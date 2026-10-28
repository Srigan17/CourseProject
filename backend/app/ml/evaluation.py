import numpy as np
from typing import Dict, Any, Optional
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, matthews_corrcoef,
    cohen_kappa_score, mean_absolute_error, mean_squared_error, r2_score
)

def evaluate_classification(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: Optional[np.ndarray] = None
) -> Dict[str, Any]:
    """
    Evaluates multi-class or binary classification predictions.
    Strictly calculates accuracy as:
        accuracy_fraction = correct_predictions / total_predictions
        accuracy_percent = accuracy_fraction * 100.0
    
    Guarantees mathematically that:
        0.0 <= accuracy <= 1.0
        0.0 <= accuracy_percent <= 100.0
    """
    y_t = np.asarray(y_true).ravel()
    y_p = np.asarray(y_pred).ravel()

    total_predictions = int(len(y_t))
    if total_predictions == 0:
        return {
            "accuracy": 0.0,
            "accuracy_percent": 0.0,
            "correct_predictions": 0,
            "total_predictions": 0,
            "precision": 0.0,
            "recall": 0.0,
            "f1_score": 0.0,
            "macro_f1": 0.0,
            "per_class_recall": [],
            "mcc": 0.0,
            "cohen_kappa": 0.0,
            "roc_auc": None,
            "confusion_matrix": []
        }

    correct_predictions = int(np.sum(y_t == y_p))
    # Correct formula: correct_predictions / total_predictions
    raw_acc = float(correct_predictions / total_predictions)
    # Strict invariant clamp to [0.0, 1.0] to prevent any numerical anomaly
    acc = max(0.0, min(1.0, raw_acc))
    acc_percent = acc * 100.0

    weighted_prec = float(precision_score(y_t, y_p, average="weighted", zero_division=0))
    weighted_rec = float(recall_score(y_t, y_p, average="weighted", zero_division=0))
    weighted_f1 = float(f1_score(y_t, y_p, average="weighted", zero_division=0))
    macro_f1 = float(f1_score(y_t, y_p, average="macro", zero_division=0))
    
    # Per-class recall
    recalls = recall_score(y_t, y_p, average=None, zero_division=0)
    per_class_recall = [round(float(r), 4) for r in recalls]
    
    # MCC and Cohen Kappa (matching paper metrics)
    try:
        mcc = float(matthews_corrcoef(y_t, y_p))
    except Exception:
        mcc = 0.0
    try:
        kappa = float(cohen_kappa_score(y_t, y_p))
    except Exception:
        kappa = 0.0

    auc = None
    if y_prob is not None:
        try:
            num_classes = len(np.unique(y_t))
            if num_classes == 2:
                auc = float(roc_auc_score(y_t, y_prob[:, 1]))
            elif num_classes > 2 and y_prob.shape[1] >= num_classes:
                auc = float(roc_auc_score(y_t, y_prob, multi_class="ovr", average="weighted"))
        except Exception:
            auc = None

    try:
        cm = confusion_matrix(y_t, y_p).tolist()
    except Exception:
        cm = []

    return {
        "accuracy": round(acc, 4),                     # Standard fraction: 0.6874
        "accuracy_percent": round(acc_percent, 2),     # Percentage format: 68.74%
        "correct_predictions": correct_predictions,
        "total_predictions": total_predictions,
        "precision": round(weighted_prec, 4),
        "recall": round(weighted_rec, 4),
        "f1_score": round(weighted_f1, 4),
        "macro_f1": round(macro_f1, 4),
        "per_class_recall": per_class_recall,
        "mcc": round(mcc, 4),
        "cohen_kappa": round(kappa, 4),
        "roc_auc": round(auc, 4) if auc is not None else None,
        "confusion_matrix": cm
    }

def evaluate_client_model(
    model: Any,
    X: np.ndarray,
    y: np.ndarray
) -> Dict[str, Any]:
    """
    Evaluates a single client / hospital local model on its local dataset.
    Ensures that accuracy strictly reflects:
        correct_predictions / total_predictions * 100
    and never exceeds 100.0%.
    """
    if len(X) == 0 or len(y) == 0:
        return {
            "correct_predictions": 0,
            "total_predictions": 0,
            "accuracy": 0.0,
            "accuracy_percent": 0.0
        }

    y_pred = model.predict(X)
    return evaluate_classification(y, y_pred)

def evaluate_regression(
    y_true: np.ndarray,
    y_pred: np.ndarray
) -> Dict[str, Any]:
    mae = float(mean_absolute_error(y_true, y_pred))
    mse = float(mean_squared_error(y_true, y_pred))
    rmse = float(np.sqrt(mse))
    r2 = float(r2_score(y_true, y_pred))
    
    # Avoid zero division in MAPE
    denom = np.where(np.abs(y_true) < 1e-6, 1e-6, np.abs(y_true))
    mape = float(np.mean(np.abs((y_true - y_pred) / denom)))

    return {
        "mae": round(mae, 4),
        "mse": round(mse, 4),
        "rmse": round(rmse, 4),
        "r2_score": round(r2, 4),
        "mape": round(mape, 4)
    }

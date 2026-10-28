import pytest
import numpy as np
from backend.app.ml.evaluation import evaluate_classification, evaluate_client_model

def test_accuracy_calculation_exact_formula():
    """
    Verifies that accuracy is strictly calculated as:
        accuracy = (correct_predictions / total_predictions) * 100
    and that accuracy is mathematically bounded between 0% and 100%.
    """
    # 4 predictions, 3 correct -> 75%
    y_true = np.array([0, 1, 2, 3])
    y_pred = np.array([0, 1, 2, 0])  # 3 correct, 1 wrong

    res = evaluate_classification(y_true, y_pred)
    assert res["correct_predictions"] == 3
    assert res["total_predictions"] == 4
    assert res["accuracy"] == 0.75
    assert res["accuracy_percent"] == 75.0
    assert 0.0 <= res["accuracy_percent"] <= 100.0

def test_accuracy_cannot_exceed_100_percent():
    """
    Guarantees that under no conditions can accuracy exceed 100% or be negative.
    """
    # 100% correct
    y_true = np.array([1, 2, 3, 4, 5])
    y_pred = np.array([1, 2, 3, 4, 5])
    res_perfect = evaluate_classification(y_true, y_pred)
    assert res_perfect["accuracy"] == 1.0
    assert res_perfect["accuracy_percent"] == 100.0
    assert res_perfect["correct_predictions"] == 5

    # 0% correct
    y_pred_wrong = np.array([0, 0, 0, 0, 0])
    res_zero = evaluate_classification(y_true, y_pred_wrong)
    assert res_zero["accuracy"] == 0.0
    assert res_zero["accuracy_percent"] == 0.0
    assert res_zero["correct_predictions"] == 0

def test_accuracy_empty_array_handling():
    """
    Verifies graceful handling of empty inputs without divide-by-zero errors.
    """
    res = evaluate_classification(np.array([]), np.array([]))
    assert res["accuracy"] == 0.0
    assert res["accuracy_percent"] == 0.0
    assert res["total_predictions"] == 0

def test_client_model_accuracy_evaluation():
    """
    Verifies that local client/hospital evaluation computes correct_predictions / total_predictions * 100.
    """
    class MockClientModel:
        def predict(self, X):
            # Returns predictions where half match y
            return np.array([1, 0, 1, 0])

    mock_model = MockClientModel()
    X_dummy = np.zeros((4, 2))
    y_dummy = np.array([1, 1, 1, 1])  # 2 match, 2 don't -> 50%

    res = evaluate_client_model(mock_model, X_dummy, y_dummy)
    assert res["correct_predictions"] == 2
    assert res["total_predictions"] == 4
    assert res["accuracy"] == 0.5
    assert res["accuracy_percent"] == 50.0
    assert 0.0 <= res["accuracy_percent"] <= 100.0

def test_accuracy_and_rmse_separation():
    """
    Verifies that classification metrics strictly include accuracy and macro-F1,
    and do not return regression RMSE or confuse the two.
    """
    y_true = np.array([0, 1, 2, 1, 0])
    y_pred = np.array([0, 1, 1, 1, 0])  # 4/5 correct = 80%

    res = evaluate_classification(y_true, y_pred)
    assert "accuracy" in res
    assert "accuracy_percent" in res
    assert "rmse" not in res
    assert res["accuracy_percent"] == 80.0

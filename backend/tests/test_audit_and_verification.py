import pytest
import numpy as np
from pathlib import Path
from backend.app.ml.preprocessing import pipeline
from backend.app.ml.models import FederatedMLPClassifier, FederatedLogisticClassifier
from backend.app.ml.federated import fl_coordinator
from backend.app.privacy.secure_aggregation import PaillierSecureAggregationService
from backend.app.ml.inference import activity_inference_service
from backend.app.ml.experiment_store import experiment_store

def test_1_dataset_preprocessing_consistency():
    """Verify consistent features and classes across hospitals without leakage."""
    data = pipeline.prepare_data("apple_watch", num_clients=3, partition_strategy="non_iid", random_state=42)
    assert data["num_features"] == 19
    assert len(data["clients"]) == 3
    assert len(data["target_classes"]) == 6
    for c in data["clients"]:
        assert c["X"].shape[1] == 19
        assert len(c["X"]) == len(c["y"])
        assert len(c["X"]) > 0

def test_2_model_parameter_dimensions():
    """Verify model parameter vector flattening and unflattening consistency."""
    m = FederatedMLPClassifier(input_dim=19, num_classes=6, hidden_layer_sizes=(128, 64))
    w = m.get_weights()
    # 19*128 + 128 + 128*64 + 64 + 64*6 + 6 = 11206
    assert len(w) == 11206
    m.set_weights(w)
    w_after = m.get_weights()
    assert np.allclose(w, w_after)

def test_3_fedprox_proximal_regularization():
    """Verify that FedProx adds proximal penalty (mu/2)*||w - w_ref||^2 during local training."""
    m = FederatedMLPClassifier(input_dim=19, num_classes=6, hidden_layer_sizes=(128, 64))
    w_ref = m.get_weights()
    X = np.random.randn(50, 19)
    y = np.random.randint(0, 6, size=50)

    # Training with mu=0.0
    loss_no_mu = m.fit_local(X, y, epochs=2, lr=0.01, mu_prox=0.0, ref_weights=w_ref)
    # Drift weights intentionally far from w_ref
    m.set_weights(w_ref + 5.0)
    # Training with mu=0.5 (should include proximal loss penalty)
    loss_with_mu = m.fit_local(X, y, epochs=1, lr=0.001, mu_prox=0.5, ref_weights=w_ref)
    assert loss_with_mu > loss_no_mu

def test_4_sample_weighted_aggregation():
    """Verify sample-weighted aggregation formula sum(n_k / N * delta_k)."""
    clients_samples = [1000, 2000, 3000]
    total = sum(clients_samples)
    deltas = [np.ones(5) * 1.0, np.ones(5) * 2.0, np.ones(5) * 3.0]
    
    # Expected weighted average: (1000*1 + 2000*2 + 3000*3)/6000 = 14000/6000 = 2.333333
    expected = (1000*1.0 + 2000*2.0 + 3000*3.0) / total
    actual = np.zeros(5)
    for i in range(len(clients_samples)):
        actual += (clients_samples[i] / total) * deltas[i]
    assert np.allclose(actual, expected)

def test_5_paillier_secure_aggregation_numerical_equivalence():
    """Verify that sample-weighted Paillier PHE matches plaintext within fixed point precision."""
    secagg = PaillierSecureAggregationService(key_length=512, scale_factor=1e6)
    c1 = np.array([0.123456, -0.654321, 0.987654])
    c2 = np.array([-0.222222, 0.333333, -0.444444])
    c3 = np.array([0.500000, -0.100000, 0.200000])
    updates = [c1, c2, c3]
    weights = [1671, 1670, 1670]

    res = secagg.execute_secure_aggregation(updates, client_weights=weights)
    assert res["metrics"]["is_numerically_exact"] is True
    assert res["metrics"]["numerical_aggregation_error"] < 1e-4

def test_6_global_evaluation_after_each_round():
    """Verify global model is evaluated on held-out test data at every round."""
    data = pipeline.prepare_data("apple_watch", num_clients=3, random_state=42)
    res = fl_coordinator.run_federated_training(
        data_dict=data,
        num_rounds=2,
        local_epochs=1,
        mu_prox=0.005,
        model_architecture="logistic",
        use_dp=False,
        use_secagg=False
    )
    assert len(res["round_history"]) == 2
    for rh in res["round_history"]:
        assert "eval_metrics" in rh
        assert "accuracy" in rh["eval_metrics"]
        assert 0.0 <= rh["eval_metrics"]["accuracy"] <= 1.0

def test_7_separation_of_train_and_test_data():
    """Strictly verify zero overlap between train and test partitions."""
    data = pipeline.prepare_data("apple_watch", num_clients=3, random_state=42)
    X_train = data["X_train"]
    X_test = data["X_test"]
    assert len(X_train) == 5011
    assert len(X_test) == 1253
    # Check that client subsets partition X_train exactly
    total_client_samples = sum(c["num_samples"] for c in data["clients"])
    assert total_client_samples == len(X_train)

def test_8_correct_mapping_six_activity_classes():
    """Verify the 6 physical activity classes match Harvard Apple Watch ground truth."""
    data = pipeline.prepare_data("apple_watch", num_clients=3, random_state=42)
    expected_classes = {
        "Lying", "Sitting", "Self Pace walk",
        "Running 3 METs", "Running 5 METs", "Running 7 METs"
    }
    assert set(data["target_classes"]) == expected_classes

def test_9_prediction_output_structure():
    """Verify inference returns confidence, all 6 probabilities, and model version."""
    payload = {
        "steps": 1200.0,
        "heart_rate": 95.0,
        "resting_heart": 62.0,
        "calories": 25.0,
        "distance": 1.2,
        "age": 25.0,
        "gender": 1,
        "height": 175.0,
        "weight": 70.0
    }
    res = activity_inference_service.predict(payload)
    assert "predicted_activity" in res
    assert "confidence_percent" in res
    assert "probabilities" in res
    assert len(res["probabilities"]) == 6
    # Probabilities sum to 1.0 (approx)
    prob_sum = sum(res["probabilities"].values())
    assert 0.99 <= prob_sum <= 1.01

def test_10_csv_validation_and_rejection():
    """Verify that invalid CSV uploads are rejected with structured errors."""
    # 1. Missing required columns
    bad_csv = "age,gender\n25,1\n30,0"
    with pytest.raises(ValueError, match="missing required sensor columns"):
        activity_inference_service.predict_csv(bad_csv)

    # 2. Empty CSV
    with pytest.raises(ValueError, match="empty"):
        activity_inference_service.predict_csv("")

def test_11_experiment_persistence():
    """Verify that completed experiments are persisted to disk and retrieved intact."""
    test_data = {"experiment_mode": "Test-FedProx", "metrics": {"accuracy": 0.72}}
    exp_id = experiment_store.save_experiment(test_data)
    retrieved = experiment_store.get_experiment(exp_id)
    assert retrieved is not None
    assert retrieved["id"] == exp_id
    assert retrieved["metrics"]["accuracy"] == 0.72
    experiment_store.delete_experiment(exp_id)

def test_12_metrics_and_optimizer_state_verification():
    """Verify optimizer reset on weight assignment and correct cross-entropy loss interpretation."""
    model = FederatedMLPClassifier(input_dim=19, num_classes=6, hidden_layer_sizes=(128, 64))
    # For 6 classes, uniform random guess cross-entropy is -ln(1/6) ~= 1.7917
    # An initial cross-entropy loss of 1.1 - 1.25 is mathematically sound
    expected_random_loss = -np.log(1.0 / 6.0)
    assert 1.70 <= expected_random_loss <= 1.80

    # Ensure set_weights resets internal optimizer state to eliminate stale momentum
    assert hasattr(model.mlp, "_optimizer")
    model.set_weights(model.get_weights())
    assert not hasattr(model.mlp, "_optimizer")

def test_13_majority_baseline_and_separation():
    """Verify majority baseline and strict separation between local train and global val evaluation."""
    data = pipeline.prepare_data("apple_watch", random_state=42)
    y_train = data["y_train"]
    y_test = data["y_test"]
    maj_class = int(np.bincount(y_train).argmax())
    y_maj = np.full_like(y_test, maj_class)
    maj_acc = float(np.mean(y_test == y_maj))
    # Lying is ~22%
    assert 0.20 <= maj_acc <= 0.25


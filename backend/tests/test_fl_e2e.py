import pytest
from backend.app.ml.preprocessing import pipeline
from backend.app.ml.centralized import run_centralized_experiment
from backend.app.ml.federated import fl_coordinator

def test_centralized_learning_baseline():
    data = pipeline.prepare_data(dataset_id="apple_watch", num_clients=3)
    res = run_centralized_experiment(data, epochs=4, lr=0.05)
    assert res["task"] == "classification"
    assert "accuracy" in res["metrics"]
    assert res["metrics"]["accuracy"] > 0.25  # Well above random chance (0.16) for 6 classes

def test_federated_learning_standard():
    data = pipeline.prepare_data(dataset_id="apple_watch", num_clients=3)
    res = fl_coordinator.run_federated_training(
        data_dict=data,
        num_rounds=2,
        local_epochs=1,
        use_dp=False,
        use_secagg=False
    )
    assert res["rounds_completed"] == 2
    assert "accuracy" in res["metrics"]
    assert len(res["round_history"]) == 2

def test_federated_learning_with_secagg_and_dp():
    data = pipeline.prepare_data(dataset_id="apple_watch", num_clients=3)
    res = fl_coordinator.run_federated_training(
        data_dict=data,
        num_rounds=2,
        local_epochs=1,
        model_architecture="logistic",
        use_dp=True,
        dp_clipping_norm=1.0,
        dp_noise_multiplier=0.3,
        use_secagg=True
    )
    assert res["differential_privacy_enabled"] is True
    assert res["secure_aggregation_enabled"] is True
    assert res["dp_budget"]["is_private"] is True
    assert "accuracy" in res["metrics"]

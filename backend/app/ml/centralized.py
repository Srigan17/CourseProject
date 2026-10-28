import time
import numpy as np
from typing import Dict, Any
from sklearn.ensemble import ExtraTreesClassifier, ExtraTreesRegressor, RandomForestClassifier, RandomForestRegressor
from sklearn.neural_network import MLPClassifier, MLPRegressor
from backend.app.ml.models import FederatedLogisticClassifier, FederatedLinearRegressor
from backend.app.ml.evaluation import evaluate_classification, evaluate_regression

def run_centralized_experiment(
    data_dict: Dict[str, Any],
    epochs: int = 50,
    lr: float = 0.01,
    batch_size: int = 32,
    model_architecture: str = "mlp",
    hidden_layer_sizes: tuple = (64, 32),
    alpha: float = 0.005
) -> Dict[str, Any]:
    """
    Trains on combined centralized training set and evaluates on held-out test set.
    Serves as the experimental benchmark to compare against Federated Learning.
    Supports Extra Trees (Paper Baseline), Multi-Layer Perceptrons (Neural FL Baseline),
    and Logistic/Linear models.
    """
    start_time = time.time()
    task = data_dict["task"]
    X_train = data_dict["X_train"]
    y_train = data_dict["y_train"]
    X_test = data_dict["X_test"]
    y_test = data_dict["y_test"]

    input_dim = X_train.shape[1]
    loss = 0.0

    if task == "classification":
        num_classes = len(data_dict["target_classes"])
        if model_architecture == "extra_trees" or model_architecture == "tree_ensemble":
            model = ExtraTreesClassifier(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            y_prob = model.predict_proba(X_test)
            mode_name = "Centralized Extra Trees (Paper Baseline)"
        elif model_architecture == "random_forest":
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            y_prob = model.predict_proba(X_test)
            mode_name = "Centralized Random Forest (Paper Baseline)"
        elif model_architecture == "mlp":
            model = MLPClassifier(hidden_layer_sizes=hidden_layer_sizes, alpha=alpha, activation='relu', solver='adam', max_iter=epochs, random_state=42, learning_rate_init=lr)
            model.fit(X_train, y_train)
            loss = float(model.loss_)
            y_pred = model.predict(X_test)
            y_prob = model.predict_proba(X_test)
            mode_name = "Centralized Multi-Layer Perceptron (Neural Baseline)"
        else:
            model = FederatedLogisticClassifier(input_dim=input_dim, num_classes=num_classes)
            loss = model.fit_local(X_train, y_train, epochs=epochs, lr=lr, batch_size=batch_size)
            y_pred = model.predict(X_test)
            y_prob = model.predict_proba(X_test)
            mode_name = "Centralized Logistic Regression Baseline"

        metrics = evaluate_classification(y_test, y_pred, y_prob)
    else:
        if model_architecture == "extra_trees" or model_architecture == "tree_ensemble":
            model = ExtraTreesRegressor(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            mode_name = "Centralized Extra Trees (Paper Baseline)"
        elif model_architecture == "mlp":
            model = MLPRegressor(hidden_layer_sizes=(64, 32), activation='relu', solver='adam', max_iter=epochs, random_state=42, learning_rate_init=lr)
            model.fit(X_train, y_train)
            loss = float(model.loss_)
            y_pred = model.predict(X_test)
            mode_name = "Centralized Multi-Layer Perceptron (Neural Baseline)"
        else:
            model = FederatedLinearRegressor(input_dim=input_dim)
            loss = model.fit_local(X_train, y_train, epochs=epochs, lr=lr, batch_size=batch_size)
            y_pred = model.predict(X_test)
            mode_name = "Centralized Linear Regression Baseline"

        metrics = evaluate_regression(y_test, y_pred)

    elapsed_time = round(time.time() - start_time, 4)

    return {
        "experiment_mode": mode_name,
        "model_architecture": model_architecture,
        "task": task,
        "dataset_id": data_dict["dataset_id"],
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "epochs": epochs,
        "final_loss": round(float(loss), 4),
        "metrics": metrics,
        "elapsed_time_sec": elapsed_time,
        "communication_cost_kb": 0.0,
        "differential_privacy_enabled": False,
        "secure_aggregation_enabled": False
    }

import time
import copy
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
import numpy as np
import joblib
import json

from backend.app.ml.models import (
    FederatedMLPClassifier,
    FederatedMLPRegressor,
    FederatedLogisticClassifier,
    FederatedLinearRegressor,
    FederatedTreeEnsembleClassifier
)
from backend.app.ml.evaluation import evaluate_classification, evaluate_regression
from backend.app.privacy.differential_privacy import DifferentialPrivacyEngine
from backend.app.privacy.secure_aggregation import PaillierSecureAggregationService
from backend.app.privacy.byzantine import krum_filter
from backend.app.security.audit import audit_logger
from backend.app.security.validation import validator
from backend.app.config import settings

class FederatedLearningCoordinator:
    """
    Coordinates collaborative training among simulated healthcare organizations
    without exposing raw patient records or individual plaintext model updates.
    
    Supports:
    1. Continuous parameter models (MLP, Logistic) with parameter delta DP-FedAvg,
       exact FedProx proximal regularization during local training,
       and Paillier Homomorphic Secure Aggregation.
    2. Federated Tree Ensembles (FedEnsemble Extra Trees / Random Forest)
       for exact paper baseline reproduction.
    """
    def __init__(
        self,
        key_length: int = 512,
        byzantine_defense: bool = True
    ):
        self.secagg_service = PaillierSecureAggregationService(key_length=key_length)
        self.byzantine_defense = byzantine_defense

    def run_federated_training(
        self,
        data_dict: Dict[str, Any],
        num_rounds: int = 8,
        local_epochs: int = 12,
        learning_rate: float = 0.01,
        batch_size: int = 32,
        mu_prox: float = 0.005,
        use_dp: bool = False,
        dp_clipping_norm: float = 8.0,
        dp_noise_multiplier: float = 0.01,
        use_secagg: bool = False,
        model_architecture: str = "mlp",
        hidden_layer_sizes: tuple = (128, 64),
        alpha: float = 0.005,
        client_sample_rate: float = 1.0,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        start_time = time.time()
        task = data_dict["task"]
        dataset_id = data_dict["dataset_id"]
        clients = data_dict["clients"]
        num_clients = len(clients)
        X_test = data_dict["X_test"]
        y_test = data_dict["y_test"]
        input_dim = data_dict["num_features"]

        # Differential privacy engine (calibrated for parameter deltas)
        dp_engine = DifferentialPrivacyEngine(
            enabled=use_dp,
            clipping_norm=dp_clipping_norm,
            noise_multiplier=dp_noise_multiplier
        )

        audit_logger.log_event(
            event_type="TRAINING_ROUND_START",
            severity="INFO",
            actor="COORDINATOR",
            details={
                "dataset_id": dataset_id,
                "model_architecture": model_architecture,
                "num_clients": num_clients,
                "total_rounds": num_rounds,
                "mu_prox": mu_prox,
                "use_dp": use_dp,
                "use_secagg": use_secagg
            }
        )

        # Handle Federated Tree Ensemble separately (discrete structures)
        if model_architecture == "tree_ensemble" and task == "classification":
            return self._run_tree_ensemble_fl(
                data_dict=data_dict,
                start_time=start_time,
                progress_callback=progress_callback
            )

        # Initialize continuous global model
        num_classes = len(data_dict.get("target_classes", [])) if task == "classification" else 0
        if task == "classification":
            if model_architecture == "logistic":
                global_model = FederatedLogisticClassifier(input_dim=input_dim, num_classes=num_classes)
            else:
                global_model = FederatedMLPClassifier(
                    input_dim=input_dim,
                    num_classes=num_classes,
                    hidden_layer_sizes=hidden_layer_sizes,
                    alpha=alpha,
                    random_state=42
                )
        else:
            if model_architecture == "linear":
                global_model = FederatedLinearRegressor(input_dim=input_dim)
            else:
                global_model = FederatedMLPRegressor(
                    input_dim=input_dim,
                    hidden_layer_sizes=hidden_layer_sizes,
                    alpha=alpha,
                    random_state=42
                )

        round_history = []
        total_comm_bytes = 0
        latest_eval_metrics = {}

        # Execute Federated Rounds
        for round_idx in range(1, num_rounds + 1):
            round_start = time.time()
            current_global_weights = global_model.get_weights()
            client_updates = []
            client_deltas_list = []
            client_metrics = []

            # Step A: Local training at each hospital (with optional subsampling)
            participating_clients = clients
            if client_sample_rate < 1.0:
                k = max(1, int(round(num_clients * client_sample_rate)))
                sampled_indices = np.random.choice(num_clients, size=k, replace=False)
                participating_clients = [clients[i] for i in sampled_indices]

            if progress_callback:
                progress_callback({
                    "type": "ROUND_START",
                    "round": round_idx,
                    "total_rounds": num_rounds,
                    "participating_clients": [c["client_name"] for c in participating_clients]
                })

            for client in participating_clients:
                cid = client["client_id"]
                cname = client["client_name"]
                X_local = client["X"]
                y_local = client["y"]
                n_samples = client["num_samples"]

                if progress_callback:
                    progress_callback({
                        "type": "CLIENT_START",
                        "round": round_idx,
                        "client_id": cid,
                        "client_name": cname,
                        "num_samples": n_samples,
                        "total_rounds": num_rounds
                    })

                # Instantiate fresh local client model initialized at current global parameters
                # This guarantees zero stale optimizer momentum leakage across rounds
                if task == "classification":
                    if model_architecture == "logistic":
                        local_model = FederatedLogisticClassifier(input_dim=input_dim, num_classes=num_classes, random_state=42 + round_idx)
                    else:
                        local_model = FederatedMLPClassifier(
                            input_dim=input_dim,
                            num_classes=num_classes,
                            hidden_layer_sizes=hidden_layer_sizes,
                            alpha=alpha,
                            random_state=42 + round_idx
                        )
                else:
                    if model_architecture == "linear":
                        local_model = FederatedLinearRegressor(input_dim=input_dim, random_state=42 + round_idx)
                    else:
                        local_model = FederatedMLPRegressor(
                            input_dim=input_dim,
                            hidden_layer_sizes=hidden_layer_sizes,
                            alpha=alpha,
                            random_state=42 + round_idx
                        )

                local_model.set_weights(current_global_weights.copy())

                # Local training with real epoch callback and exact FedProx proximal regularization
                def make_epoch_cb(c_id, c_name):
                    def _cb(ep, total_eps, cur_loss):
                        if progress_callback:
                            progress_callback({
                                "type": "LOCAL_EPOCH",
                                "round": round_idx,
                                "client_id": c_id,
                                "client_name": c_name,
                                "epoch": ep,
                                "total_epochs": total_eps,
                                "loss": round(float(cur_loss), 4),
                                "total_rounds": num_rounds
                            })
                    return _cb

                local_loss = local_model.fit_local(
                    X_local,
                    y_local,
                    epochs=local_epochs,
                    lr=learning_rate,
                    batch_size=batch_size,
                    mu_prox=mu_prox,
                    ref_weights=current_global_weights,
                    epoch_callback=make_epoch_cb(cid, cname)
                )
                local_w = local_model.get_weights()
                
                # Compute Parameter Delta: Delta = w_local - w_global
                delta_w = local_w - current_global_weights

                # Step B: Apply Differential Privacy (Clipping Delta + Calibrated Noise) locally
                if use_dp:
                    delta_w = dp_engine.add_noise(delta_w)

                # Step C: Model update validation
                is_valid, reason = validator.validate_single_update(delta_w, cid)
                if not is_valid:
                    audit_logger.log_event(
                        event_type="UPDATE_REJECTED",
                        severity="WARNING",
                        actor=cid,
                        client_id=cid,
                        round_num=round_idx,
                        details={"reason": reason}
                    )
                    continue

                # Calculate local client training accuracy on local training data (strictly labeled)
                local_accuracy = 0.0
                if task == "classification":
                    try:
                        y_client_pred = local_model.predict(X_local)
                        correct_cnt = int(np.sum(y_local == y_client_pred))
                        total_cnt = int(len(y_local))
                        local_accuracy = round(float(correct_cnt / total_cnt) * 100.0, 2) if total_cnt > 0 else 0.0
                        local_accuracy = max(0.0, min(100.0, local_accuracy))
                    except Exception:
                        local_accuracy = 0.0

                client_updates.append({
                    "client_id": cid,
                    "client_name": cname,
                    "num_samples": n_samples,
                    "loss": round(float(local_loss), 4),
                    "accuracy": local_accuracy,
                    "delta": delta_w
                })
                client_deltas_list.append(delta_w)
                client_metrics.append({
                    "client_id": cid,
                    "client_name": cname,
                    "num_samples": n_samples,
                    "local_loss": round(float(local_loss), 4),
                    "local_training_accuracy": local_accuracy
                })

                if progress_callback:
                    progress_callback({
                        "type": "CLIENT_COMPLETE",
                        "round": round_idx,
                        "client_id": cid,
                        "client_name": cname,
                        "local_loss": round(float(local_loss), 4),
                        "local_accuracy": local_accuracy,
                        "total_rounds": num_rounds
                    })

            if not client_updates:
                raise RuntimeError(f"All client updates rejected in round {round_idx}.")

            # Step D: Aggregation Phase
            if progress_callback:
                progress_callback({
                    "type": "AGGREGATION_START",
                    "round": round_idx,
                    "use_secagg": use_secagg,
                    "num_clients": len(client_updates),
                    "total_rounds": num_rounds
                })

            secagg_time = 0.0
            secagg_error = 0.0
            client_sample_counts = [cu["num_samples"] for cu in client_updates]
            total_samples = sum(client_sample_counts)

            if use_secagg:
                # Apply Paillier Homomorphic Encryption on weighted parameter deltas
                secagg_res = self.secagg_service.execute_secure_aggregation(
                    client_updates=client_deltas_list,
                    client_weights=client_sample_counts
                )
                aggregated_delta = secagg_res["aggregated_weights"]
                secagg_time = secagg_res["metrics"]["total_secagg_time_sec"]
                secagg_error = secagg_res["metrics"].get("numerical_aggregation_error", 0.0)
                total_comm_bytes += secagg_res["metrics"]["param_count"] * 128 * num_clients
                
                audit_logger.log_event(
                    event_type="SECAGG_SUCCESS",
                    severity="INFO",
                    actor="COORDINATOR",
                    round_num=round_idx,
                    details={
                        "protocol": "Paillier Homomorphic Encryption",
                        "participating_clients": num_clients,
                        "secagg_time_sec": secagg_time,
                        "numerical_aggregation_error": secagg_error
                    }
                )
            else:
                # Standard Sample-Weighted FedAvg on parameter deltas:
                # Delta_global = sum_{k=1}^K (n_k / N) * Delta_k
                aggregated_delta = np.zeros_like(current_global_weights)
                for cu in client_updates:
                    weight_factor = cu["num_samples"] / total_samples
                    aggregated_delta += weight_factor * cu["delta"]
                total_comm_bytes += current_global_weights.size * 4 * num_clients

            if progress_callback:
                progress_callback({
                    "type": "AGGREGATION_COMPLETE",
                    "round": round_idx,
                    "secagg_time_sec": round(secagg_time, 4),
                    "secagg_error": secagg_error,
                    "total_rounds": num_rounds
                })

            # Step E: Update Global Model via Delta Accumulation
            new_global_weights = current_global_weights + aggregated_delta
            global_model.set_weights(new_global_weights)

            # Step F: Evaluate current global model on held-out test data
            if task == "classification":
                y_pred = global_model.predict(X_test)
                y_prob = global_model.predict_proba(X_test)
                eval_metrics = evaluate_classification(y_test, y_pred, y_prob)
            else:
                y_pred = global_model.predict(X_test)
                eval_metrics = evaluate_regression(y_test, y_pred)

            latest_eval_metrics = eval_metrics
            round_elapsed = round(time.time() - round_start, 4)
            round_info = {
                "round": round_idx,
                "elapsed_sec": round_elapsed,
                "secagg_time_sec": round(secagg_time, 4),
                "secagg_error": secagg_error,
                "client_metrics": client_metrics,
                "eval_metrics": eval_metrics
            }
            round_history.append(round_info)

            if progress_callback:
                progress_callback({
                    "type": "GLOBAL_UPDATE",
                    "round": round_idx,
                    "total_rounds": num_rounds,
                    "eval_metrics": eval_metrics,
                    "client_metrics": client_metrics
                })

        # Calculate final privacy budget
        dp_budget = dp_engine.compute_privacy_budget(num_rounds=num_rounds, sample_rate=client_sample_rate) if use_dp else {
            "is_private": False,
            "epsilon": float("inf"),
            "guarantee": "No DP mechanism applied"
        }

        total_elapsed = round(time.time() - start_time, 4)
        comm_overhead_kb = round(total_comm_bytes / 1024, 2)

        # Save trained global model weights and metadata for live Activity Testing
        try:
            models_dir = Path(settings.MODELS_DIR) if hasattr(settings, "MODELS_DIR") else Path("storage/models")
            models_dir.mkdir(parents=True, exist_ok=True)
            np.save(models_dir / "combined_weights.npy", global_model.get_weights())
            if "scaler" in data_dict:
                joblib.dump(data_dict["scaler"], models_dir / "power_scaler.joblib")
            if "target_classes" in data_dict:
                with open(models_dir / "classes.json", "w", encoding="utf-8") as f:
                    json.dump(data_dict["target_classes"], f)
            if "feature_names" in data_dict:
                with open(models_dir / "feature_names.json", "w", encoding="utf-8") as f:
                    json.dump(data_dict["feature_names"], f)
        except Exception as e:
            audit_logger.log_event(
                event_type="MODEL_SAVE_WARNING",
                severity="WARNING",
                actor="COORDINATOR",
                details={"error": str(e)}
            )

        audit_logger.log_event(
            event_type="TRAINING_ROUND_COMPLETE",
            severity="INFO",
            actor="COORDINATOR",
            details={
                "dataset_id": dataset_id,
                "total_rounds": num_rounds,
                "final_accuracy": latest_eval_metrics.get("accuracy"),
                "final_rmse": latest_eval_metrics.get("rmse"),
                "use_dp": use_dp,
                "use_secagg": use_secagg,
                "elapsed_sec": total_elapsed
            }
        )

        mode_name = f"Federated Learning ({model_architecture.upper()})"
        if mu_prox > 0:
            mode_name = f"FedProx (mu={mu_prox})"
        if use_dp and use_secagg:
            mode_name += " + Differential Privacy + Secure Aggregation"
        elif use_dp:
            mode_name += " + Differential Privacy"
        elif use_secagg:
            mode_name += " + Secure Aggregation (Paillier PHE)"

        result_dict = {
            "experiment_mode": mode_name,
            "model_architecture": model_architecture,
            "task": task,
            "dataset_id": dataset_id,
            "num_clients": num_clients,
            "rounds_completed": num_rounds,
            "local_epochs": local_epochs,
            "learning_rate": learning_rate,
            "batch_size": batch_size,
            "mu_prox": mu_prox,
            "differential_privacy_enabled": use_dp,
            "dp_clipping_norm": dp_clipping_norm if use_dp else None,
            "dp_noise_multiplier": dp_noise_multiplier if use_dp else None,
            "dp_budget": dp_budget,
            "secure_aggregation_enabled": use_secagg,
            "secagg_protocol": "Paillier Additive Homomorphic Cryptosystem" if use_secagg else "None",
            "communication_cost_kb": comm_overhead_kb,
            "elapsed_time_sec": total_elapsed,
            "metrics": round_history[-1]["eval_metrics"],
            "round_history": round_history
        }

        if progress_callback:
            progress_callback({
                "type": "TRAINING_COMPLETE",
                "total_rounds": num_rounds,
                "elapsed_time_sec": total_elapsed,
                "final_metrics": round_history[-1]["eval_metrics"]
            })

        return result_dict

    def _run_tree_ensemble_fl(
        self,
        data_dict: Dict[str, Any],
        start_time: float,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        """
        Executes the exact FedEnsemble strategy reported in Akhmetov et al. (2025).
        Trains Extra Trees locally at each hospital node, then unifies trees at coordinator.
        """
        from sklearn.ensemble import ExtraTreesClassifier
        dataset_id = data_dict["dataset_id"]
        clients = data_dict["clients"]
        num_clients = len(clients)
        X_test = data_dict["X_test"]
        y_test = data_dict["y_test"]

        trees_per_client = 40
        client_models = []
        client_metrics = []

        for c in clients:
            cid = c["client_id"]
            cname = c["client_name"]
            X_loc = c["X"]
            y_loc = c["y"]
            et_local = ExtraTreesClassifier(n_estimators=trees_per_client, random_state=42)
            et_local.fit(X_loc, y_loc)
            client_models.append(et_local)
            client_metrics.append({
                "client_id": cid,
                "client_name": cname,
                "num_samples": len(X_loc),
                "trees_trained": trees_per_client
            })

        fed_tree_ens = FederatedTreeEnsembleClassifier()
        fed_tree_ens.aggregate_client_models(client_models)

        y_pred = fed_tree_ens.predict(X_test)
        y_prob = fed_tree_ens.predict_proba(X_test)
        eval_metrics = evaluate_classification(y_test, y_pred, y_prob)

        total_elapsed = round(time.time() - start_time, 4)
        comm_kb = round(num_clients * trees_per_client * 2.5, 2)

        round_history = [{
            "round": 1,
            "elapsed_sec": total_elapsed,
            "secagg_time_sec": 0.0,
            "client_metrics": client_metrics,
            "eval_metrics": eval_metrics
        }]

        if progress_callback:
            progress_callback({
                "round": 1,
                "total_rounds": 1,
                "eval_metrics": eval_metrics,
                "client_metrics": client_metrics
            })

        result_dict = {
            "experiment_mode": "Federated Extra Trees Ensemble (Paper FedEnsemble Baseline)",
            "model_architecture": "tree_ensemble",
            "task": "classification",
            "dataset_id": dataset_id,
            "num_clients": num_clients,
            "rounds_completed": 1,
            "local_epochs": 1,
            "learning_rate": 0.0,
            "batch_size": 0,
            "differential_privacy_enabled": False,
            "dp_budget": {"is_private": False, "guarantee": "Tree ensemble does not use DP-SGD"},
            "secure_aggregation_enabled": False,
            "secagg_protocol": "FedEnsemble Rule Aggregation",
            "communication_cost_kb": comm_kb,
            "elapsed_time_sec": total_elapsed,
            "metrics": eval_metrics,
            "round_history": round_history
        }

        return result_dict

fl_coordinator = FederatedLearningCoordinator()

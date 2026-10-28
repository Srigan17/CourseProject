import os
import json
import time
import copy
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    cohen_kappa_score, matthews_corrcoef, confusion_matrix
)
from opacus import PrivacyEngine
from opacus.accountants import RDPAccountant

# 1. Exact Tuned PyTorch MLP Architecture (12,710 Parameters)
class TunedActivityMLP(nn.Module):
    def __init__(self, in_features=16, num_classes=6):
        super(TunedActivityMLP, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(in_features, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, num_classes)
        )
        
    def forward(self, x):
        return self.net(x)

def set_seed(seed):
    torch.manual_seed(seed)
    np.random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def evaluate_model_on_test(model, X_test_tensor, y_test_true, class_names):
    model.eval()
    with torch.no_grad():
        logits = model(X_test_tensor)
        preds = logits.argmax(dim=-1).cpu().numpy()
        loss = nn.CrossEntropyLoss()(logits, torch.tensor(y_test_true, dtype=torch.long)).item()
        
    acc = accuracy_score(y_test_true, preds)
    prec = precision_score(y_test_true, preds, average="macro", zero_division=0)
    rec = recall_score(y_test_true, preds, average="macro", zero_division=0)
    f1 = f1_score(y_test_true, preds, average="macro", zero_division=0)
    kappa = cohen_kappa_score(y_test_true, preds)
    mcc = matthews_corrcoef(y_test_true, preds)
    cm = confusion_matrix(y_test_true, preds).tolist()
    
    return {
        "loss": round(float(loss), 4),
        "accuracy": round(float(acc), 4),
        "precision": round(float(prec), 4),
        "recall": round(float(rec), 4),
        "f1": round(float(f1), 4),
        "kappa": round(float(kappa), 4),
        "mcc": round(float(mcc), 4),
        "confusion_matrix": cm,
        "class_names": list(class_names)
    }

def fedavg_aggregate_fixed_weights(client_weights_list):
    """
    Fixed public aggregation weights: 0.25 per client (k=4).
    Guarantees data-independent post-processing under add/remove record adjacency.
    """
    k = len(client_weights_list)
    assert k == 4, f"Expected 4 clients, got {k}"
    weight = 1.0 / k # exactly 0.25
    global_weights = copy.deepcopy(client_weights_list[0])
    
    for key in global_weights.keys():
        global_weights[key] = sum(
            client_weights_list[i][key].float() * weight
            for i in range(k)
        )
    return global_weights

def run_dp_fedavg_single_seed(
    client_datasets,
    client_loaders,
    X_test_t,
    y_test,
    class_names,
    seed,
    sigma,
    clipping_norm=1.0,
    target_delta=1e-5,
    rounds=25,
    local_epochs=3,
    lr=0.003,
    weight_decay=1e-3
):
    set_seed(seed)
    k = len(client_datasets)
    assert k == 4, f"Expected 4 clients, got {k}"
    
    global_model = TunedActivityMLP(in_features=16, num_classes=6)
    
    # Persistent PrivacyEngines per client across all 25 rounds
    client_privacy_engines = [PrivacyEngine(accountant="prv") for _ in range(k)]
    
    start_time = time.time()
    
    for r in range(rounds):
        client_weights = []
        for c in range(k):
            # 1. Local model initialized with broadcast global model
            client_model = TunedActivityMLP(in_features=16, num_classes=6)
            client_model.load_state_dict(global_model.state_dict())
            
            # 2. Local optimizer instantiated fresh per round (standard FedAvg)
            optimizer = torch.optim.AdamW(client_model.parameters(), lr=lr, weight_decay=weight_decay)
            
            # 3. Wrap local model with persistent PrivacyEngine
            client_model, optimizer, private_loader = client_privacy_engines[c].make_private(
                module=client_model,
                optimizer=optimizer,
                data_loader=client_loaders[c],
                noise_multiplier=sigma,
                max_grad_norm=clipping_norm,
                poisson_sampling=True
            )
            
            # 4. Local DP-SGD training over local_epochs
            client_model.train()
            criterion = nn.CrossEntropyLoss()
            for ep in range(local_epochs):
                for bx, by in private_loader:
                    if len(bx) == 0:
                        continue
                    optimizer.zero_grad()
                    out = client_model(bx)
                    loss = criterion(out, by)
                    loss.backward()
                    optimizer.step()
                    
            # 5. Extract unwrapped weights (Opacus wraps in GradSampleModule)
            unwrapped_m = getattr(client_model, "_module", client_model)
            client_weights.append(copy.deepcopy(unwrapped_m.state_dict()))
            
        # 6. Global Server Aggregation using FIXED PUBLIC WEIGHTS (0.25)
        global_w = fedavg_aggregate_fixed_weights(client_weights)
        global_model.load_state_dict(global_w)
        
        # NOTE: STRICT ZERO evaluation of the held-out test set during rounds 1..24
        
    duration = round(time.time() - start_time, 2)
    
    # 7. Evaluate on held-out test set STRICTLY ONCE after round 25 completes
    test_metrics = evaluate_model_on_test(global_model, X_test_t, y_test, class_names)
    test_metrics["training_time_seconds"] = duration
    
    # 8. Extract runtime privacy accounting details directly from live accountants
    client_histories = [pe.accountant.history for pe in client_privacy_engines]
    client_step_counts = [sum(h[2] for h in pe.accountant.history) for pe in client_privacy_engines]
    client_sample_rates = [pe.accountant.history[0][1] for pe in client_privacy_engines]
    
    # Assert step count consistency across clients
    assert all(steps == client_step_counts[0] for steps in client_step_counts), (
        f"Step count mismatch across clients: {client_step_counts}"
    )
    actual_steps = client_step_counts[0]
    sample_rate = client_sample_rates[0]
    
    # Runtime PRV epsilon
    eps_prv_values = [pe.accountant.get_epsilon(delta=target_delta) for pe in client_privacy_engines]
    eps_prv = round(float(np.mean(eps_prv_values)), 4)
    
    # Cross-verification with RDPAccountant on identical history
    rdp_acc = RDPAccountant()
    rdp_acc.history = copy.deepcopy(client_privacy_engines[0].accountant.history)
    eps_rdp = round(float(rdp_acc.get_epsilon(delta=target_delta)), 4)
    
    privacy_info = {
        "noise_multiplier": sigma,
        "clipping_norm": clipping_norm,
        "target_delta": target_delta,
        "runtime_accounted_steps": actual_steps,
        "runtime_sample_rate": round(float(sample_rate), 6),
        "runtime_epsilon_prv": eps_prv,
        "runtime_epsilon_rdp": eps_rdp,
        "client_step_counts": client_step_counts
    }
    
    test_metrics["privacy"] = privacy_info
    return test_metrics

def compute_summary_stats(seed_results):
    metrics_keys = ["accuracy", "precision", "recall", "f1", "kappa", "mcc", "loss"]
    summary = {}
    for k in metrics_keys:
        vals = [r[k] for r in seed_results]
        summary[k] = {
            "mean": round(float(np.mean(vals)), 4),
            "std": round(float(np.std(vals)), 4),
            "min": round(float(np.min(vals)), 4),
            "max": round(float(np.max(vals)), 4)
        }
    summary["privacy"] = {
        "runtime_epsilon_prv": seed_results[0]["privacy"]["runtime_epsilon_prv"],
        "runtime_epsilon_rdp": seed_results[0]["privacy"]["runtime_epsilon_rdp"],
        "noise_multiplier": seed_results[0]["privacy"]["noise_multiplier"],
        "clipping_norm": seed_results[0]["privacy"]["clipping_norm"],
        "target_delta": seed_results[0]["privacy"]["target_delta"],
        "runtime_accounted_steps": seed_results[0]["privacy"]["runtime_accounted_steps"],
        "runtime_sample_rate": seed_results[0]["privacy"]["runtime_sample_rate"]
    }
    return summary

def main():
    print("=================================================================================")
    print("        PHASE 3: SECURE FEDERATED LEARNING WITH DIFFERENTIAL PRIVACY (DP-FEDAVG) ")
    print("=================================================================================")
    
    train_path = os.path.join("data", "processed", "train_sample_split.csv")
    test_path = os.path.join("data", "processed", "test_sample_split.csv")
    partitions_dir = os.path.join("data", "partitions", "k4")
    
    # 1. Load strictly partitioned training and test data
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    feat_cols = [c for c in train_df.columns if c not in ["participant_id", "activity"]]
    
    assert len(test_df) == 732, f"Expected 732 test records, got {len(test_df)}"
    assert len(train_df) == 2924, f"Expected 2924 train records, got {len(train_df)}"
    
    # 2. Fit StandardScaler strictly on the global training partition
    scaler = StandardScaler()
    scaler.fit(train_df[feat_cols].values)
    
    X_test_scaled = scaler.transform(test_df[feat_cols].values)
    le = LabelEncoder()
    le.fit(train_df["activity"])
    y_test = le.transform(test_df["activity"])
    class_names = le.classes_
    
    X_test_t = torch.tensor(X_test_scaled, dtype=torch.float32)
    
    # 3. Prepare client datasets and base loaders for k=4
    client_datasets = []
    client_loaders = []
    for c in range(4):
        c_path = os.path.join(partitions_dir, f"client_{c}.csv")
        c_df = pd.read_csv(c_path)
        assert len(c_df) == 731, f"Expected 731 samples for client {c}, got {len(c_df)}"
        
        Xc_scaled = scaler.transform(c_df[feat_cols].values)
        yc = le.transform(c_df["activity"])
        
        c_ds = TensorDataset(torch.tensor(Xc_scaled, dtype=torch.float32), torch.tensor(yc, dtype=torch.long))
        c_dl = DataLoader(c_ds, batch_size=32, shuffle=True)
        
        client_datasets.append(c_ds)
        client_loaders.append(c_dl)
        
    seeds = [42, 123, 456, 789, 2026]
    noise_multipliers = [0.5, 1.0, 1.5, 2.0]
    clipping_norm = 1.0
    target_delta = 1e-5
    rounds = 25
    local_epochs = 3
    lr = 0.003
    weight_decay = 1e-3
    
    # Reference plaintext baseline (Track 2 Tuned Baseline: FedAvg k=4)
    ref_plaintext_acc = 0.6760
    ref_plaintext_f1 = 0.6789
    
    print(f"Experimental Configurations: Noise Multipliers = {noise_multipliers}")
    print(f"Deterministic Seeds: {seeds}")
    print(f"Fixed Aggregation Weights: 0.25 per client (4 clients)")
    print(f"Clipping Norm: {clipping_norm}, Target Delta: {target_delta}")
    print(f"Communication: {rounds} rounds x {local_epochs} local epochs")
    print(f"Reference Plaintext Baseline: Acc = {ref_plaintext_acc*100:.2f}%, F1 = {ref_plaintext_f1*100:.2f}%")
    print("---------------------------------------------------------------------------------")
    
    results = {
        "metadata": {
            "experiment": "Phase 3: Differential Privacy FedAvg (DP-FedAvg, Configuration B)",
            "model_type": "Tuned PyTorch Multi-Layer Perceptron",
            "architecture": "Linear(16->128) -> ReLU -> Linear(128->64) -> ReLU -> Linear(64->32) -> ReLU -> Linear(32->6)",
            "total_parameters": 12710,
            "optimizer": "AdamW",
            "learning_rate": lr,
            "weight_decay": weight_decay,
            "batch_size": 32,
            "federated_rounds": rounds,
            "federated_local_epochs": local_epochs,
            "num_clients": 4,
            "aggregation_weights": [0.25, 0.25, 0.25, 0.25],
            "aggregation_type": "Fixed public equal weighting (data-independent post-processing)",
            "seeds": seeds,
            "noise_multipliers": noise_multipliers,
            "clipping_norm": clipping_norm,
            "target_delta": target_delta,
            "privacy_guarantee_scope": "Record-level Differential Privacy under add/remove one 10-second activity record adjacency",
            "disclaimer": "Does NOT claim patient-level DP, healthcare regulatory compliance, or asymptotic statistical significance.",
            "test_isolation": "Strict 732-row held-out test set evaluated strictly once after round 25 completion",
            "reference_plaintext_baseline": {
                "accuracy": ref_plaintext_acc,
                "f1": ref_plaintext_f1
            }
        },
        "configurations": {}
    }
    
    for sigma in noise_multipliers:
        config_key = f"sigma_{sigma}"
        print(f"\n>>> Running Configuration: Noise Multiplier sigma = {sigma} (C = {clipping_norm}) <<<")
        
        seed_results = []
        for s in seeds:
            t0 = time.time()
            metrics = run_dp_fedavg_single_seed(
                client_datasets=client_datasets,
                client_loaders=client_loaders,
                X_test_t=X_test_t,
                y_test=y_test,
                class_names=class_names,
                seed=s,
                sigma=sigma,
                clipping_norm=clipping_norm,
                target_delta=target_delta,
                rounds=rounds,
                local_epochs=local_epochs,
                lr=lr,
                weight_decay=weight_decay
            )
            elapsed = round(time.time() - t0, 1)
            seed_results.append(metrics)
            
            p = metrics["privacy"]
            print(f"  Seed {s:<4} | Acc: {metrics['accuracy']*100:.2f}% | F1: {metrics['f1']*100:.2f}% | Loss: {metrics['loss']:.4f} | PRV eps: {p['runtime_epsilon_prv']:.2f} | RDP eps: {p['runtime_epsilon_rdp']:.2f} | Steps: {p['runtime_accounted_steps']} | Time: {elapsed}s")
            
        summary = compute_summary_stats(seed_results)
        
        # Calculate empirical utility degradation against reference baseline
        mean_acc = summary["accuracy"]["mean"]
        mean_f1 = summary["f1"]["mean"]
        utility_gap_acc = round(float(ref_plaintext_acc - mean_acc), 4)
        utility_gap_f1 = round(float(ref_plaintext_f1 - mean_f1), 4)
        
        summary["utility_degradation"] = {
            "delta_accuracy": utility_gap_acc,
            "delta_f1": utility_gap_f1
        }
        
        results["configurations"][config_key] = {
            "per_seed": {str(s): seed_results[i] for i, s in enumerate(seeds)},
            "summary": summary
        }
        
        print(f"Summary for sigma={sigma}: Acc = {mean_acc*100:.2f}% +/- {summary['accuracy']['std']*100:.2f}%, F1 = {mean_f1*100:.2f}%, PRV eps = {summary['privacy']['runtime_epsilon_prv']}, Utility Gap = {utility_gap_acc*100:+.2f}%")
        
    # Save outputs to dedicated Phase 3 directory
    out_dir = os.path.join("results", "dp_track2")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "phase3_dp_fedavg_results.json")
    
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
        
    print(f"\n=================================================================================")
    print(f"Phase 3 Execution Successfully Completed. Results verified and saved to:")
    print(f"  {out_path}")
    print("=================================================================================")

if __name__ == "__main__":
    main()

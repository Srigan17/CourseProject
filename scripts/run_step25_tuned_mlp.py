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

# Tuned High-Capacity PyTorch MLP Architecture
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

def evaluate_pytorch_model(model, X_test_tensor, y_test_true, class_names):
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

def train_local_client(model, dataloader, epochs, lr, seed):
    set_seed(seed)
    model.train()
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-3)
    criterion = nn.CrossEntropyLoss()
    
    for epoch in range(epochs):
        for bx, by in dataloader:
            optimizer.zero_grad()
            out = model(bx)
            loss = criterion(out, by)
            loss.backward()
            optimizer.step()
            
    return model.state_dict()

def fedavg_aggregate(client_weights_list, client_sizes):
    total_samples = sum(client_sizes)
    global_weights = copy.deepcopy(client_weights_list[0])
    
    for key in global_weights.keys():
        global_weights[key] = sum(
            client_weights_list[i][key].float() * (client_sizes[i] / total_samples)
            for i in range(len(client_weights_list))
        )
    return global_weights

def run_centralized_tuned_mlp(X_train, y_train, X_test_t, y_test, class_names, seed, epochs=80, batch_size=32, lr=0.003):
    set_seed(seed)
    model = TunedActivityMLP(in_features=16, num_classes=6)
    
    X_tr_t = torch.tensor(X_train, dtype=torch.float32)
    y_tr_t = torch.tensor(y_train, dtype=torch.long)
    dataset = TensorDataset(X_tr_t, y_tr_t)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-2)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    criterion = nn.CrossEntropyLoss()
    
    loss_history = []
    
    start_t = time.time()
    for epoch in range(epochs):
        model.train()
        ep_loss = 0.0
        for bx, by in loader:
            optimizer.zero_grad()
            out = model(bx)
            loss = criterion(out, by)
            loss.backward()
            optimizer.step()
            ep_loss += loss.item() * len(bx)
        scheduler.step()
        loss_history.append(round(ep_loss / len(X_train), 4))
        
    duration = round(time.time() - start_t, 2)
    metrics = evaluate_pytorch_model(model, X_test_t, y_test, class_names)
    metrics["training_time_seconds"] = duration
    metrics["train_loss_history"] = loss_history
    return metrics

def run_federated_tuned_mlp(client_data_tensors, X_test_t, y_test, class_names, seed, k, rounds=25, local_epochs=3, batch_size=32, lr=0.003):
    set_seed(seed)
    global_model = TunedActivityMLP(in_features=16, num_classes=6)
    client_sizes = [len(c[1]) for c in client_data_tensors]
    
    round_test_losses = []
    round_test_accs = []
    
    start_t = time.time()
    for r in range(rounds):
        client_weights = []
        for i in range(k):
            client_model = TunedActivityMLP(in_features=16, num_classes=6)
            client_model.load_state_dict(global_model.state_dict())
            
            c_loader = DataLoader(
                TensorDataset(client_data_tensors[i][0], client_data_tensors[i][1]),
                batch_size=batch_size,
                shuffle=True
            )
            
            w_updated = train_local_client(client_model, c_loader, epochs=local_epochs, lr=lr, seed=seed + r * 10 + i)
            client_weights.append(w_updated)
            
        # FedAvg Aggregation
        global_w = fedavg_aggregate(client_weights, client_sizes)
        global_model.load_state_dict(global_w)
        
        # Track round progress
        with torch.no_grad():
            global_model.eval()
            r_logits = global_model(X_test_t)
            r_loss = nn.CrossEntropyLoss()(r_logits, torch.tensor(y_test, dtype=torch.long)).item()
            r_acc = (r_logits.argmax(dim=-1).cpu().numpy() == y_test).mean()
            round_test_losses.append(round(float(r_loss), 4))
            round_test_accs.append(round(float(r_acc), 4))
            
    duration = round(time.time() - start_t, 2)
    metrics = evaluate_pytorch_model(global_model, X_test_t, y_test, class_names)
    metrics["training_time_seconds"] = duration
    metrics["round_test_losses"] = round_test_losses
    metrics["round_test_accs"] = round_test_accs
    return metrics

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
    return summary

def main():
    print("================== STEP 2.5: TUNED PYTORCH MLP BASELINE EXECUTION ==================")
    train_path = os.path.join("data", "processed", "train_sample_split.csv")
    test_path = os.path.join("data", "processed", "test_sample_split.csv")
    partitions_dir = os.path.join("data", "partitions")
    
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    feat_cols = [c for c in train_df.columns if c not in ["participant_id", "activity"]]
    
    # 1. Fit StandardScaler STRICTLY on the 2,924-row training partition
    scaler = StandardScaler()
    X_train_raw = train_df[feat_cols].values
    X_test_raw = test_df[feat_cols].values
    
    X_train_scaled = scaler.fit_transform(X_train_raw)
    X_test_scaled = scaler.transform(X_test_raw)
    
    le = LabelEncoder()
    y_train = le.fit_transform(train_df["activity"])
    y_test = le.transform(test_df["activity"])
    class_names = le.classes_
    
    X_test_t = torch.tensor(X_test_scaled, dtype=torch.float32)
    
    seeds = [42, 123, 456, 789, 2026]
    print(f"Executing Tuned MLP across 5 seeds: {seeds}")
    
    results = {
        "metadata": {
            "model_type": "Tuned PyTorch Multi-Layer Perceptron (Track 2 Baseline)",
            "architecture": "Linear(16->128) -> ReLU -> Linear(128->64) -> ReLU -> Linear(64->32) -> ReLU -> Linear(32->6)",
            "total_parameters": 12710,
            "optimizer": "AdamW",
            "centralized_lr": 0.003,
            "centralized_weight_decay": 1e-2,
            "centralized_epochs": 80,
            "centralized_scheduler": "CosineAnnealingLR(T_max=80)",
            "federated_lr": 0.003,
            "federated_weight_decay": 1e-3,
            "federated_rounds": 25,
            "federated_local_epochs": 3,
            "batch_size": 32,
            "seeds": seeds,
            "client_configurations": [2, 4, 8],
            "partitioning_nature": "Approximate IID random subsets (shuffled chunks)",
            "test_isolation": "Strict 732-row held-out test set, zero training or scaling leakage"
        },
        "centralized": {},
        "federated": {}
    }
    
    # Centralized Tuned MLP
    print("\n--- Running Centralized Tuned MLP across 5 seeds ---")
    cl_seed_results = []
    for s in seeds:
        m = run_centralized_tuned_mlp(X_train_scaled, y_train, X_test_t, y_test, class_names, seed=s)
        cl_seed_results.append(m)
        print(f"  Seed {s}: Acc={m['accuracy']}, F1={m['f1']}, Kappa={m['kappa']}, Loss={m['loss']}, Time={m['training_time_seconds']}s")
        
    results["centralized"] = {
        "per_seed": {str(s): cl_seed_results[i] for i, s in enumerate(seeds)},
        "summary": compute_summary_stats(cl_seed_results)
    }
    
    # Federated Tuned MLP for k in [2, 4, 8]
    for k in [2, 4, 8]:
        print(f"\n--- Running Federated Tuned MLP (k = {k}, FedAvg) across 5 seeds ---")
        k_dir = os.path.join(partitions_dir, f"k{k}")
        
        # Load and scale each client partition using the GLOBAL training scaler
        client_tensors = []
        for c in range(k):
            c_df = pd.read_csv(os.path.join(k_dir, f"client_{c}.csv"))
            Xc_raw = c_df[feat_cols].values
            yc = le.transform(c_df["activity"])
            Xc_scaled = scaler.transform(Xc_raw) # Consistently scaled
            
            client_tensors.append((
                torch.tensor(Xc_scaled, dtype=torch.float32),
                torch.tensor(yc, dtype=torch.long)
            ))
            
        fl_seed_results = []
        for s in seeds:
            m = run_federated_tuned_mlp(client_tensors, X_test_t, y_test, class_names, seed=s, k=k)
            fl_seed_results.append(m)
            print(f"  [k={k}] Seed {s}: Acc={m['accuracy']}, F1={m['f1']}, Kappa={m['kappa']}, Loss={m['loss']}, Time={m['training_time_seconds']}s")
            
        results["federated"][f"k{k}"] = {
            "per_seed": {str(s): fl_seed_results[i] for i, s in enumerate(seeds)},
            "summary": compute_summary_stats(fl_seed_results)
        }
        
    # Save tuned results separately
    out_dir = os.path.join("results", "baseline_track2")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "track2_tuned_mlp_baseline_results.json")
    
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
        
    print(f"\nTuned MLP execution complete. Verified results saved to {out_path}")

if __name__ == "__main__":
    main()

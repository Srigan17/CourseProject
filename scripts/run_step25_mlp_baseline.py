import os
import json
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

# 1. Standard PyTorch Multi-Layer Perceptron (MLP) Architecture
class ActivityMLP(nn.Module):
    def __init__(self, in_features=16, num_classes=6):
        super(ActivityMLP, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(in_features, 64),
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
        
    acc = accuracy_score(y_test_true, preds)
    prec = precision_score(y_test_true, preds, average="macro", zero_division=0)
    rec = recall_score(y_test_true, preds, average="macro", zero_division=0)
    f1 = f1_score(y_test_true, preds, average="macro", zero_division=0)
    kappa = cohen_kappa_score(y_test_true, preds)
    mcc = matthews_corrcoef(y_test_true, preds)
    cm = confusion_matrix(y_test_true, preds).tolist()
    
    return {
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
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)
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

def run_centralized_mlp(X_train, y_train, X_test_t, y_test, class_names, seed, epochs=60, batch_size=32, lr=0.003):
    set_seed(seed)
    model = ActivityMLP(in_features=16, num_classes=6)
    
    X_tr_t = torch.tensor(X_train, dtype=torch.float32)
    y_tr_t = torch.tensor(y_train, dtype=torch.long)
    dataset = TensorDataset(X_tr_t, y_tr_t)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)
    criterion = nn.CrossEntropyLoss()
    
    model.train()
    for epoch in range(epochs):
        for bx, by in loader:
            optimizer.zero_grad()
            out = model(bx)
            loss = criterion(out, by)
            loss.backward()
            optimizer.step()
            
    metrics = evaluate_pytorch_model(model, X_test_t, y_test, class_names)
    return metrics

def run_federated_mlp(client_data_tensors, X_test_t, y_test, class_names, seed, k, rounds=20, local_epochs=3, batch_size=32, lr=0.003):
    set_seed(seed)
    global_model = ActivityMLP(in_features=16, num_classes=6)
    client_sizes = [len(c[1]) for c in client_data_tensors]
    
    for r in range(rounds):
        client_weights = []
        for i in range(k):
            client_model = ActivityMLP(in_features=16, num_classes=6)
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
        
    metrics = evaluate_pytorch_model(global_model, X_test_t, y_test, class_names)
    return metrics

def compute_summary_stats(seed_results):
    metrics_keys = ["accuracy", "precision", "recall", "f1", "kappa", "mcc"]
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
    print("================== STEP 2.5: PYTORCH MLP BASELINE ESTABLISHMENT ==================")
    train_path = os.path.join("data", "processed", "train_sample_split.csv")
    test_path = os.path.join("data", "processed", "test_sample_split.csv")
    partitions_dir = os.path.join("data", "partitions")
    
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    feat_cols = [c for c in train_df.columns if c not in ["participant_id", "activity"]]
    
    # 1. Fit StandardScaler STRICTLY on the training partition
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
    
    print(f"Features: {len(feat_cols)}, Training rows: {len(X_train_scaled)}, Test rows: {len(X_test_scaled)}")
    print(f"Target Classes: {list(class_names)}")
    
    seeds = [42, 123, 456, 789, 2026]
    print(f"Deterministic Evaluation Seeds: {seeds}")
    
    results = {
        "metadata": {
            "model_type": "PyTorch Multi-Layer Perceptron (Track 2 Baseline)",
            "architecture": "Linear(16->64) -> ReLU -> Linear(64->32) -> ReLU -> Linear(32->6)",
            "optimizer": "Adam",
            "learning_rate": 0.003,
            "weight_decay": 1e-4,
            "batch_size": 32,
            "centralized_epochs": 60,
            "federated_rounds": 20,
            "federated_local_epochs": 3,
            "seeds": seeds,
            "client_configurations": [2, 4, 8],
            "partitioning_nature": "Approximate IID random subsets (shuffled chunks)",
            "test_isolation": "Strict 732-row held-out test set, zero training or scaling leakage"
        },
        "centralized": {},
        "federated": {}
    }
    
    # Run Centralized MLP
    print("\n--- Running Centralized MLP across 5 seeds ---")
    cl_seed_results = []
    for s in seeds:
        m = run_centralized_mlp(X_train_scaled, y_train, X_test_t, y_test, class_names, seed=s)
        cl_seed_results.append(m)
        print(f"  Seed {s}: Acc={m['accuracy']}, F1={m['f1']}, Kappa={m['kappa']}")
        
    results["centralized"] = {
        "per_seed": {str(s): cl_seed_results[i] for i, s in enumerate(seeds)},
        "summary": compute_summary_stats(cl_seed_results)
    }
    
    # Run Federated MLP for k in [2, 4, 8]
    for k in [2, 4, 8]:
        print(f"\n--- Running Federated MLP (k = {k}, FedAvg) across 5 seeds ---")
        k_dir = os.path.join(partitions_dir, f"k{k}")
        
        # Load and scale each client partition using the GLOBAL training scaler
        client_tensors = []
        for c in range(k):
            c_df = pd.read_csv(os.path.join(k_dir, f"client_{c}.csv"))
            Xc_raw = c_df[feat_cols].values
            yc = le.transform(c_df["activity"])
            Xc_scaled = scaler.transform(Xc_raw) # Preprocessing applied consistently
            
            client_tensors.append((
                torch.tensor(Xc_scaled, dtype=torch.float32),
                torch.tensor(yc, dtype=torch.long)
            ))
            
        fl_seed_results = []
        for s in seeds:
            m = run_federated_mlp(client_tensors, X_test_t, y_test, class_names, seed=s, k=k)
            fl_seed_results.append(m)
            print(f"  [k={k}] Seed {s}: Acc={m['accuracy']}, F1={m['f1']}, Kappa={m['kappa']}")
            
        results["federated"][f"k{k}"] = {
            "per_seed": {str(s): fl_seed_results[i] for i, s in enumerate(seeds)},
            "summary": compute_summary_stats(fl_seed_results)
        }
        
    # Save final Step 2.5 results
    out_dir = os.path.join("results", "baseline_track2")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "track2_mlp_baseline_results.json")
    
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
        
    print(f"\nStep 2.5 Track 2 MLP Baseline complete. Results saved to {out_path}")

if __name__ == "__main__":
    main()

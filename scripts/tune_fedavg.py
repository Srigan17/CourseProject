import torch
import torch.nn as nn
import pandas as pd
import numpy as np
import copy
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, f1_score

train_df = pd.read_csv("data/processed/train_sample_split.csv")
feat_cols = [c for c in train_df.columns if c not in ["participant_id", "activity"]]
le = LabelEncoder()
y_all = le.fit_transform(train_df["activity"])
X_all = train_df[feat_cols].values

X_tr, X_val, y_tr, y_val = train_test_split(X_all, y_all, test_size=0.20, random_state=42, stratify=y_all)
scaler = StandardScaler()
X_tr_s = scaler.fit_transform(X_tr)
X_val_s = scaler.transform(X_val)

def build_model():
    return nn.Sequential(
        nn.Linear(16, 128), nn.ReLU(),
        nn.Linear(128, 64), nn.ReLU(),
        nn.Linear(64, 32), nn.ReLU(),
        nn.Linear(32, 6)
    )

def fedavg(weights_list, sizes):
    total = sum(sizes)
    global_w = copy.deepcopy(weights_list[0])
    for k in global_w.keys():
        global_w[k] = sum(weights_list[i][k].float() * (sizes[i] / total) for i in range(len(weights_list)))
    return global_w

# Split X_tr_s into k=4 clients
split_idxs = np.array_split(np.arange(len(X_tr_s)), 4)
clients_data = [(torch.tensor(X_tr_s[idx], dtype=torch.float32), torch.tensor(y_tr[idx], dtype=torch.long)) for idx in split_idxs]
sizes = [len(idx) for idx in split_idxs]

configs = [
    ("adam_003_r20_e3", "adam", 0.003, 20, 3),
    ("adamw_001_r25_e2", "adamw", 0.001, 25, 2),
    ("sgd_01_r30_e2", "sgd", 0.01, 30, 2),
    ("adamw_cos_r30_e2", "adamw_cos", 0.0015, 30, 2)
]

for name, opt_type, lr, r_count, l_ep in configs:
    torch.manual_seed(42)
    global_m = build_model()
    crit = nn.CrossEntropyLoss()
    
    for r in range(r_count):
        client_w = []
        cur_lr = lr * (0.5 * (1 + np.cos(np.pi * r / r_count))) if opt_type == "adamw_cos" else lr
        for c in range(4):
            cm = build_model()
            cm.load_state_dict(global_m.state_dict())
            cm.train()
            if opt_type == "sgd":
                opt = torch.optim.SGD(cm.parameters(), lr=cur_lr, momentum=0.9, weight_decay=1e-4)
            else:
                opt = torch.optim.AdamW(cm.parameters(), lr=cur_lr, weight_decay=1e-3)
            
            loader = torch.utils.data.DataLoader(torch.utils.data.TensorDataset(clients_data[c][0], clients_data[c][1]), batch_size=32, shuffle=True)
            for ep in range(l_ep):
                for bx, by in loader:
                    opt.zero_grad()
                    loss = crit(cm(bx), by)
                    loss.backward()
                    opt.step()
            client_w.append(cm.state_dict())
        
        global_m.load_state_dict(fedavg(client_w, sizes))
    
    global_m.eval()
    with torch.no_grad():
        preds = global_m(torch.tensor(X_val_s, dtype=torch.float32)).argmax(dim=-1).numpy()
        acc = accuracy_score(y_val, preds)
        f1 = f1_score(y_val, preds, average="macro")
        print(f"FedAvg k=4 {name} -> Val Acc: {acc:.4f}, Val F1: {f1:.4f}")

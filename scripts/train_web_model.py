import os
import sys
sys.path.insert(0, os.path.abspath("."))
import torch
import torch.nn as nn
import pandas as pd
import numpy as np
import pickle
from torch.utils.data import DataLoader, TensorDataset
from scripts.run_phase4_secagg import TunedActivityMLP, custom_secagg_aggregate, set_seed

def main():
    set_seed(42)
    train_path = os.path.join("data", "processed", "train_sample_split.csv")
    test_path = os.path.join("data", "processed", "test_sample_split.csv")
    partitions_dir = os.path.join("data", "partitions", "k4")
    
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    feat_cols = [c for c in train_df.columns if c not in ["participant_id", "activity"]]
    
    with open("web/model/scaler.pkl", "rb") as f:
        scaler = pickle.load(f)
    with open("web/model/label_encoder.pkl", "rb") as f:
        le = pickle.load(f)
        
    X_test_scaled = scaler.transform(test_df[feat_cols].values)
    y_test = le.transform(test_df["activity"])
    X_test_t = torch.tensor(X_test_scaled, dtype=torch.float32)
    y_test_t = torch.tensor(y_test, dtype=torch.long)
    
    # Load client datasets
    client_loaders = []
    for c in range(4):
        c_df = pd.read_csv(os.path.join(partitions_dir, f"client_{c}.csv"))
        Xc_scaled = scaler.transform(c_df[feat_cols].values)
        yc = le.transform(c_df["activity"])
        ds = TensorDataset(torch.tensor(Xc_scaled, dtype=torch.float32), torch.tensor(yc, dtype=torch.long))
        client_loaders.append(DataLoader(ds, batch_size=32, shuffle=True))
        
    global_model = TunedActivityMLP(in_features=16, num_classes=6)
    
    # Run 25 rounds of Federated Averaging with SecAgg
    print("Training web inference model across 25 federated SecAgg rounds...")
    for r in range(25):
        client_weights = []
        for c in range(4):
            client_model = TunedActivityMLP(in_features=16, num_classes=6)
            client_model.load_state_dict(global_model.state_dict())
            optimizer = torch.optim.AdamW(client_model.parameters(), lr=0.003, weight_decay=1e-3)
            client_model.train()
            criterion = nn.CrossEntropyLoss()
            for ep in range(3):
                for bx, by in client_loaders[c]:
                    optimizer.zero_grad()
                    out = client_model(bx)
                    loss = criterion(out, by)
                    loss.backward()
                    optimizer.step()
            client_weights.append(client_model.state_dict())
            
        global_w = custom_secagg_aggregate(client_weights)
        global_model.load_state_dict(global_w)
        
    global_model.eval()
    with torch.no_grad():
        preds = global_model(X_test_t).argmax(dim=-1).numpy()
        acc = (preds == y_test).mean()
        print(f"Model trained successfully! Test Accuracy: {acc*100:.2f}%")
        
    torch.save(global_model.state_dict(), "web/model/model_tuned_mlp.pt")
    print("Saved model checkpoint to web/model/model_tuned_mlp.pt")

if __name__ == "__main__":
    main()

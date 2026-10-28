import os
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    cohen_kappa_score, matthews_corrcoef, confusion_matrix
)
from imblearn.over_sampling import SMOTE
import copy

def load_data():
    train_path = os.path.join("data", "processed", "train_sample_split.csv")
    test_path = os.path.join("data", "processed", "test_sample_split.csv")
    
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    
    # Feature columns (exclude synthetic participant_id and target activity)
    feat_cols = [c for c in train_df.columns if c not in ["participant_id", "activity"]]
    
    # Encode target activity labels
    le = LabelEncoder()
    y_train = le.fit_transform(train_df["activity"])
    y_test = le.transform(test_df["activity"])
    
    X_train = train_df[feat_cols].values
    X_test = test_df[feat_cols].values
    
    return X_train, y_train, X_test, y_test, feat_cols, le

def evaluate_model(model, X_test, y_test, class_names):
    y_pred = model.predict(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average="macro", zero_division=0)
    rec = recall_score(y_test, y_pred, average="macro", zero_division=0)
    f1 = f1_score(y_test, y_pred, average="macro", zero_division=0)
    kappa = cohen_kappa_score(y_test, y_pred)
    mcc = matthews_corrcoef(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred).tolist()
    
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

def run_centralized(X_train, y_train, X_test, y_test, class_names, seed=42):
    print("\n================== CENTRALIZED LEARNING BASELINE ==================")
    # 1. Apply SMOTE strictly on training data
    sm = SMOTE(random_state=seed)
    X_train_res, y_train_res = sm.fit_resample(X_train, y_train)
    print(f"Train samples before SMOTE: {len(X_train)}, after SMOTE: {len(X_train_res)}")
    
    # Extra Trees
    et_cl = ExtraTreesClassifier(n_estimators=100, random_state=seed)
    et_cl.fit(X_train_res, y_train_res)
    et_metrics = evaluate_model(et_cl, X_test, y_test, class_names)
    print(f"Centralized Extra Trees (ET): Acc={et_metrics['accuracy']}, F1={et_metrics['f1']}, Kappa={et_metrics['kappa']}, MCC={et_metrics['mcc']}")
    
    # Random Forest
    rf_cl = RandomForestClassifier(n_estimators=100, random_state=seed)
    rf_cl.fit(X_train_res, y_train_res)
    rf_metrics = evaluate_model(rf_cl, X_test, y_test, class_names)
    print(f"Centralized Random Forest (RF): Acc={rf_metrics['accuracy']}, F1={rf_metrics['f1']}, Kappa={rf_metrics['kappa']}, MCC={rf_metrics['mcc']}")
    
    return {"et": et_metrics, "rf": rf_metrics}

def run_federated_experiments(X_test, y_test, feat_cols, le, class_names, seed=42):
    partitions_dir = os.path.join("data", "partitions")
    results = {}
    
    for k in [2, 4, 8]:
        print(f"\n================== FEDERATED EXPERIMENTS (k = {k}) ==================")
        k_dir = os.path.join(partitions_dir, f"k{k}")
        
        # Load each client data
        clients_data = []
        for c in range(k):
            c_file = os.path.join(k_dir, f"client_{c}.csv")
            c_df = pd.read_csv(c_file)
            X_c = c_df[feat_cols].values
            y_c = le.transform(c_df["activity"])
            
            # Apply SMOTE locally within client
            sm = SMOTE(random_state=seed + c)
            X_c_res, y_c_res = sm.fit_resample(X_c, y_c)
            clients_data.append((X_c_res, y_c_res))
            
        for model_name, ModelClass in [("et", ExtraTreesClassifier), ("rf", RandomForestClassifier)]:
            client_models = []
            client_val_scores = []
            
            # Train each client model locally
            # In standard 100-tree model, each client fits trees
            n_trees_per_client = max(10, 100 // k)
            
            for c in range(k):
                X_c_res, y_c_res = clients_data[c]
                # Client fits local model
                # Model A (full 100 trees for selection)
                m_full = ModelClass(n_estimators=100, random_state=seed + c)
                m_full.fit(X_c_res, y_c_res)
                
                # Internal validation score on client data (OOB or train accuracy)
                val_acc = m_full.score(X_c_res, y_c_res)
                client_models.append(m_full)
                client_val_scores.append(val_acc)
                
            # Mechanism A: Author's FedEnsemble Strategy (Select Best Performing Client Model)
            best_client_idx = int(np.argmax(client_val_scores))
            best_model = client_models[best_client_idx]
            metrics_selection = evaluate_model(best_model, X_test, y_test, class_names)
            
            # Mechanism B: Federated Ensemble Combining Trees Across Hospitals
            # Combine estimators_ from all clients into a single global forest
            combined_model = ModelClass(n_estimators=n_trees_per_client * k, random_state=seed)
            # Fit dummy on small data to initialize attributes
            combined_model.fit(clients_data[0][0][:10], clients_data[0][1][:10])
            combined_estimators = []
            for c in range(k):
                m_sub = ModelClass(n_estimators=n_trees_per_client, random_state=seed + c)
                m_sub.fit(clients_data[c][0], clients_data[c][1])
                combined_estimators.extend(m_sub.estimators_)
                
            combined_model.estimators_ = combined_estimators
            combined_model.n_estimators = len(combined_estimators)
            combined_model.classes_ = np.array(range(len(class_names)))
            combined_model.n_classes_ = len(class_names)
            metrics_combined = evaluate_model(combined_model, X_test, y_test, class_names)
            
            print(f"[{model_name.upper()}] k={k} Author's FedEnsemble Selection (Client {best_client_idx}): Acc={metrics_selection['accuracy']}, F1={metrics_selection['f1']}, Kappa={metrics_selection['kappa']}")
            print(f"[{model_name.upper()}] k={k} Combined Forest Ensemble (Trees={len(combined_estimators)}): Acc={metrics_combined['accuracy']}, F1={metrics_combined['f1']}, Kappa={metrics_combined['kappa']}")
            
            results[f"{model_name}_k{k}"] = {
                "author_selection_strategy": metrics_selection,
                "combined_forest_ensemble": metrics_combined,
                "best_client_idx": best_client_idx
            }
            
    return results

def main():
    X_train, y_train, X_test, y_test, feat_cols, le = load_data()
    class_names = le.classes_
    print(f"Classes: {class_names}")
    print(f"X_train shape: {X_train.shape}, X_test shape: {X_test.shape}")
    
    # Run Centralized Baseline
    cl_results = run_centralized(X_train, y_train, X_test, y_test, class_names, seed=42)
    
    # Run Federated Experiments
    fl_results = run_federated_experiments(X_test, y_test, feat_cols, le, class_names, seed=42)
    
    # Save results
    output_dir = os.path.join("results", "baseline_track1")
    os.makedirs(output_dir, exist_ok=True)
    
    all_results = {
        "dataset": "Harvard Apple Watch (Fuller et al., 2020 / BMJ Open 2021)",
        "train_rows": len(X_train),
        "test_rows": len(X_test),
        "features": feat_cols,
        "classes": list(class_names),
        "seed": 42,
        "centralized": cl_results,
        "federated": fl_results
    }
    
    out_file = os.path.join(output_dir, "track1_tree_baseline_results.json")
    with open(out_file, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nAll Step 2.4 Track 1 Baseline results saved to {out_file}")

if __name__ == "__main__":
    main()

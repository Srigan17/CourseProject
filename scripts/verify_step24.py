import os
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    cohen_kappa_score, matthews_corrcoef, confusion_matrix, log_loss
)
from imblearn.over_sampling import SMOTE

def verify_data_integrity():
    print("=== DATA INTEGRITY & ISOLATION AUDIT ===")
    train_path = os.path.join("data", "processed", "train_sample_split.csv")
    test_path = os.path.join("data", "processed", "test_sample_split.csv")
    
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    
    print(f"Primary Train Set: {len(train_df)} rows")
    print(f"Held-Out Test Set: {len(test_df)} rows")
    assert len(train_df) == 2924, "Train set row count mismatch"
    assert len(test_df) == 732, "Test set row count mismatch"
    assert train_df.isnull().sum().sum() == 0, "Null values found in train set"
    assert test_df.isnull().sum().sum() == 0, "Null values found in test set"
    
    # Verify client partitions for k in [2, 4, 8]
    partitions_dir = os.path.join("data", "partitions")
    for k in [2, 4, 8]:
        k_dir = os.path.join(partitions_dir, f"k{k}")
        client_dfs = [pd.read_csv(os.path.join(k_dir, f"client_{c}.csv")) for c in range(k)]
        total_k_rows = sum(len(cdf) for cdf in client_dfs)
        assert total_k_rows == 2924, f"Sum of client rows for k={k} is {total_k_rows}, expected 2924"
        
        # Verify no test rows inside client partitions
        feat_cols = [c for c in train_df.columns if c not in ["participant_id", "activity"]]
        combined_clients_df = pd.concat(client_dfs, ignore_index=True)
        overlap_with_test = pd.merge(combined_clients_df[feat_cols], test_df[feat_cols], how="inner")
        assert len(overlap_with_test) == 0, f"DATA LEAKAGE: {len(overlap_with_test)} test rows found in client partitions for k={k}!"
        print(f"k={k}: {total_k_rows} rows across {k} clients verified. Zero overlap with test set.")
        
    print("Integrity Audit Passed: Zero leakage, zero nulls, exact row counts confirmed.\n")
    return train_df, test_df, feat_cols

def evaluate_predictions(y_true, y_pred, class_names):
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, average="macro", zero_division=0)
    rec = recall_score(y_true, y_pred, average="macro", zero_division=0)
    f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)
    kappa = cohen_kappa_score(y_true, y_pred)
    mcc = matthews_corrcoef(y_true, y_pred)
    cm = confusion_matrix(y_true, y_pred).tolist()
    
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

def run_verified_experiments():
    train_df, test_df, feat_cols = verify_data_integrity()
    
    le = LabelEncoder()
    y_train_full = le.fit_transform(train_df["activity"])
    y_test_full = le.transform(test_df["activity"])
    X_train_full = train_df[feat_cols].values
    X_test_full = test_df[feat_cols].values
    class_names = le.classes_
    
    seed = 42
    
    # 1. Centralized Learning
    print("=== 1. CENTRALIZED LEARNING BASELINE ===")
    sm_cl = SMOTE(random_state=seed)
    X_train_sm, y_train_sm = sm_cl.fit_resample(X_train_full, y_train_full)
    
    # Centralized Extra Trees
    et_cl = ExtraTreesClassifier(n_estimators=100, random_state=seed)
    et_cl.fit(X_train_sm, y_train_sm)
    et_cl_metrics = evaluate_predictions(y_test_full, et_cl.predict(X_test_full), class_names)
    print(f"CL Extra Trees: Acc={et_cl_metrics['accuracy']}, F1={et_cl_metrics['f1']}, Kappa={et_cl_metrics['kappa']}, MCC={et_cl_metrics['mcc']}")
    
    # Centralized Random Forest
    rf_cl = RandomForestClassifier(n_estimators=100, random_state=seed)
    rf_cl.fit(X_train_sm, y_train_sm)
    rf_cl_metrics = evaluate_predictions(y_test_full, rf_cl.predict(X_test_full), class_names)
    print(f"CL Random Forest: Acc={rf_cl_metrics['accuracy']}, F1={rf_cl_metrics['f1']}, Kappa={rf_cl_metrics['kappa']}, MCC={rf_cl_metrics['mcc']}")
    
    cl_results = {"et": et_cl_metrics, "rf": rf_cl_metrics}
    
    # 2. Federated Experiments for k in [2, 4, 8]
    fl_results = {}
    partitions_dir = os.path.join("data", "partitions")
    
    for k in [2, 4, 8]:
        print(f"\n=== 2. FEDERATED EXPERIMENTS: k = {k} ===")
        k_dir = os.path.join(partitions_dir, f"k{k}")
        
        # Load clients
        client_train_val = []
        for c in range(k):
            cdf = pd.read_csv(os.path.join(k_dir, f"client_{c}.csv"))
            Xc = cdf[feat_cols].values
            yc = le.transform(cdf["activity"])
            
            # Client internal 70/30 train/val split (mirroring PyCaret setup)
            # Stratified to ensure all classes exist in local validation for log_loss
            Xc_tr, Xc_val, yc_tr, yc_val = train_test_split(
                Xc, yc, test_size=0.30, random_state=seed + c, stratify=yc
            )
            
            # Apply SMOTE strictly on client local 70% train split
            sm_c = SMOTE(random_state=seed + c)
            Xc_tr_sm, yc_tr_sm = sm_c.fit_resample(Xc_tr, yc_tr)
            
            client_train_val.append({
                "client_id": c,
                "Xc_tr_sm": Xc_tr_sm,
                "yc_tr_sm": yc_tr_sm,
                "Xc_val": Xc_val,
                "yc_val": yc_val,
                "full_Xc": Xc,
                "full_yc": yc
            })
            
        for model_name, ModelClass in [("et", ExtraTreesClassifier), ("rf", RandomForestClassifier)]:
            client_models = []
            client_log_losses = []
            
            # Sub-forest trees per client for combined ensemble
            n_trees_per_client = max(10, 100 // k)
            client_sub_forests = []
            
            for c in range(k):
                c_data = client_train_val[c]
                
                # --- A. Fit full 100-tree model for FedEnsemble Selection ---
                m_full = ModelClass(n_estimators=100, random_state=seed + c)
                m_full.fit(c_data["Xc_tr_sm"], c_data["yc_tr_sm"])
                
                # Compute local log_loss on client internal validation split
                proba_val = m_full.predict_proba(c_data["Xc_val"])
                local_loss = log_loss(c_data["yc_val"], proba_val, labels=list(range(len(class_names))))
                client_models.append(m_full)
                client_log_losses.append(local_loss)
                
                # --- B. Fit sub-forest for Combined Ensemble ---
                # Fitted on client's local SMOTE training data
                m_sub = ModelClass(n_estimators=n_trees_per_client, random_state=seed + c)
                m_sub.fit(c_data["Xc_tr_sm"], c_data["yc_tr_sm"])
                client_sub_forests.append(m_sub)
                
            # Mechanism A: FedEnsemble Selection (Minimizing Local Validation Log Loss)
            best_client_idx = int(np.argmin(client_log_losses))
            best_loss_val = round(float(client_log_losses[best_client_idx]), 4)
            best_selected_model = client_models[best_client_idx]
            metrics_selection = evaluate_predictions(y_test_full, best_selected_model.predict(X_test_full), class_names)
            metrics_selection["selected_client_id"] = best_client_idx
            metrics_selection["selected_client_local_log_loss"] = best_loss_val
            metrics_selection["all_client_local_log_losses"] = [round(float(l), 4) for l in client_log_losses]
            
            # Mechanism B: Genuine Combined Forest Ensemble
            # Construct a global ensemble combining the independent client trees
            combined_estimators = []
            for m_sub in client_sub_forests:
                combined_estimators.extend(m_sub.estimators_)
                
            combined_global = ModelClass(n_estimators=len(combined_estimators), random_state=seed)
            # Initialize internal attributes via minimal fit
            combined_global.fit(X_train_sm[:len(class_names) * 2], y_train_sm[:len(class_names) * 2])
            combined_global.estimators_ = combined_estimators
            combined_global.n_estimators = len(combined_estimators)
            combined_global.classes_ = np.array(range(len(class_names)))
            combined_global.n_classes_ = len(class_names)
            
            metrics_combined = evaluate_predictions(y_test_full, combined_global.predict(X_test_full), class_names)
            metrics_combined["total_trees"] = len(combined_estimators)
            metrics_combined["trees_per_client"] = n_trees_per_client
            
            print(f"[{model_name.upper()}] k={k} Paper Selection (Min Log Loss Client {best_client_idx}, loss={best_loss_val}): Acc={metrics_selection['accuracy']}, F1={metrics_selection['f1']}, Kappa={metrics_selection['kappa']}")
            print(f"[{model_name.upper()}] k={k} Combined Forest Ensemble ({len(combined_estimators)} trees): Acc={metrics_combined['accuracy']}, F1={metrics_combined['f1']}, Kappa={metrics_combined['kappa']}")
            
            fl_results[f"{model_name}_k{k}"] = {
                "paper_fedensemble_selection": metrics_selection,
                "combined_forest_ensemble": metrics_combined
            }
            
    # Save verified results
    out_dir = os.path.join("results", "baseline_track1")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "track1_tree_baseline_results.json")
    
    verified_data = {
        "dataset": "Harvard Apple Watch (Fuller et al., 2020 / BMJ Open 2021)",
        "train_rows": len(X_train_full),
        "test_rows": len(X_test_full),
        "features": feat_cols,
        "classes": list(class_names),
        "seed": seed,
        "partitioning_type": "IID random chunking (deterministic shuffle with seed 42)",
        "centralized": cl_results,
        "federated": fl_results
    }
    
    with open(out_path, "w") as f:
        json.dump(verified_data, f, indent=2)
    print(f"\nVerified Step 2.4 results successfully saved to {out_path}")
    return verified_data

if __name__ == "__main__":
    run_verified_experiments()

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from sklearn.model_selection import train_test_split, GroupShuffleSplit
from sklearn.preprocessing import StandardScaler, QuantileTransformer, LabelEncoder
try:
    from imblearn.over_sampling import SMOTE
    SMOTE_AVAILABLE = True
except ImportError:
    SMOTE_AVAILABLE = False

from backend.app.ml.datasets import dataset_manager, DATASET_METADATA

class PreprocessingPipeline:
    def __init__(self):
        pass

    def prepare_data(
        self,
        dataset_id: str,
        test_size: float = 0.2,
        num_clients: int = 3,
        partition_strategy: str = "non_iid",
        apply_smote: bool = False,
        scaler_type: str = "power",  # "power" (Yeo-Johnson standard for health sensor FL), "quantile", or "standard"
        split_strategy: str = "random",  # "random" (stratified paper methodology) or "group_subject"
        random_state: int = 42
    ) -> Dict[str, Any]:
        """
        Loads the real dataset, performs feature extraction, encodes labels,
        splits into 80% train / 20% test partitions, fits scalers ONLY on train (strict zero leakage),
        and distributes training data across simulated healthcare organizations.
        """
        df = dataset_manager.load_dataset(dataset_id).copy()
        meta = DATASET_METADATA[dataset_id]
        task = meta["task"]
        target_col = meta["target_col"]

        # 1. Clean missing values and drop exact duplicates
        df = df.dropna().drop_duplicates()

        # Identify subject groups for participant audit
        subject_group_ids = None
        if dataset_id == "apple_watch":
            demog_cols = [c for c in ["age", "gender", "height", "weight"] if c in df.columns]
            if demog_cols:
                subject_group_ids = df.groupby(demog_cols).ngroup().values
        elif "subject_id" in df.columns:
            subject_group_ids = df["subject_id"].values
        elif "User_ID" in df.columns:
            subject_group_ids = df["User_ID"].values

        # Drop non-predictive identifiers from features
        for col in ["Unnamed: 0", "X1", "subject_id", "User_ID", "device"]:
            if col in df.columns and col != target_col:
                df = df.drop(columns=[col])

        # 2. Separate features X and target y
        if target_col not in df.columns:
            raise ValueError(f"Target column '{target_col}' not found in dataset '{dataset_id}'.")
            
        y_raw = df[target_col].values
        X_df = df.drop(columns=[target_col])

        # 3. Handle categorical columns in X (e.g. gender)
        label_encoders = {}
        for col in X_df.select_dtypes(include=["object", "category"]).columns:
            le = LabelEncoder()
            X_df[col] = le.fit_transform(X_df[col].astype(str))
            label_encoders[col] = le

        # 3b. Physiological interaction features for activity classification
        if dataset_id == "apple_watch":
            if "hear_rate" in X_df.columns and "resting_heart" in X_df.columns:
                X_df["heart_elevation"] = X_df["hear_rate"] - X_df["resting_heart"]
            if "calories" in X_df.columns and "hear_rate" in X_df.columns:
                X_df["metabolic_intensity"] = X_df["calories"] / (X_df["hear_rate"] + 1.0)
            if "steps" in X_df.columns and "distance" in X_df.columns:
                X_df["step_cadence"] = X_df["steps"] / (X_df["distance"] + 0.001)

        X = X_df.values.astype(np.float64)
        feature_names = X_df.columns.tolist()

        # 4. Handle target variable
        target_encoder = None
        target_classes = None
        if task == "classification":
            target_encoder = LabelEncoder()
            y = target_encoder.fit_transform(y_raw.astype(str))
            target_classes = [str(c) for c in target_encoder.classes_]
        else:
            y = y_raw.astype(np.float64)

        # 5. Train / Test split
        # Note on split_strategy: In aw_fb_data.csv, no explicit participant_id column exists.
        # subject_group_ids partitions records by demographic profile tuple (age, gender, height, weight).
        # This is formally a Demographic-Profile-Group Split (not a verified biological subject ID split).
        if split_strategy in ["group_subject", "demographic_profile_group"] and subject_group_ids is not None:
            gss = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=random_state)
            train_idx, test_idx = next(gss.split(X, y, groups=subject_group_ids))
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]
        else:
            if task == "classification":
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=test_size, random_state=random_state, stratify=y
                )
            else:
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=test_size, random_state=random_state
                )

        # 6. Fit Scaler STRICTLY on X_train to prevent data leakage
        if scaler_type == "power":
            from sklearn.preprocessing import PowerTransformer
            scaler = PowerTransformer(method="yeo-johnson")
        elif scaler_type == "quantile":
            scaler = QuantileTransformer(output_distribution="normal", random_state=random_state)
        else:
            scaler = StandardScaler()

        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # 7. Optional SMOTE on training data (only for classification)
        smote_applied = False
        if apply_smote and task == "classification" and SMOTE_AVAILABLE:
            try:
                min_class_count = min(pd.Series(y_train).value_counts())
                k_neighbors = min(5, max(1, min_class_count - 1))
                if k_neighbors >= 1:
                    smote = SMOTE(k_neighbors=k_neighbors, random_state=random_state)
                    X_train_scaled, y_train = smote.fit_resample(X_train_scaled, y_train)
                    smote_applied = True
            except Exception:
                smote_applied = False

        # 8. Partition X_train across simulated healthcare clients (Hospital A, B, C...)
        client_data = self._partition_clients(
            X_train_scaled, y_train, num_clients, partition_strategy, task, random_state
        )

        return {
            "dataset_id": dataset_id,
            "task": task,
            "num_features": len(feature_names),
            "feature_names": feature_names,
            "target_classes": target_classes,
            "train_size": len(X_train_scaled),
            "test_size": len(X_test_scaled),
            "X_train": X_train_scaled,
            "y_train": y_train,
            "X_test": X_test_scaled,
            "y_test": y_test,
            "scaler": scaler,
            "scaler_type": scaler_type,
            "split_strategy": split_strategy,
            "target_encoder": target_encoder,
            "smote_applied": smote_applied,
            "clients": client_data
        }

    def _partition_clients(
        self,
        X: np.ndarray,
        y: np.ndarray,
        num_clients: int,
        strategy: str,
        task: str,
        random_state: int
    ) -> List[Dict[str, Any]]:
        client_names = [f"Hospital {chr(65 + i)}" for i in range(num_clients)]
        total_samples = len(X)
        clients = []

        if strategy == "iid":
            np.random.seed(random_state)
            indices = np.random.permutation(total_samples)
            splits = np.array_split(indices, num_clients)
            for i, split_idx in enumerate(splits):
                clients.append({
                    "client_id": f"hospital_{chr(97 + i)}",
                    "client_name": client_names[i],
                    "X": X[split_idx],
                    "y": y[split_idx],
                    "num_samples": len(split_idx),
                    "partition_strategy": "IID (Uniform Random)"
                })
        else:
            # Realistic Non-IID: Dirichlet-based class distribution skew (alpha=0.8)
            # Ensures skewed patient populations per hospital while maintaining non-zero class representation
            rng = np.random.RandomState(random_state)
            client_indices = [[] for _ in range(num_clients)]
            
            if task == "classification":
                unique_classes = np.unique(y)
                for c in unique_classes:
                    c_indices = np.where(y == c)[0]
                    rng.shuffle(c_indices)
                    # Draw Dirichlet proportions for this class across clients
                    proportions = rng.dirichlet(np.repeat(0.8, num_clients))
                    proportions = proportions / proportions.sum()
                    splits = (np.cumsum(proportions) * len(c_indices)).astype(int)[:-1]
                    class_splits = np.split(c_indices, splits)
                    for i in range(num_clients):
                        client_indices[i].extend(class_splits[i])
            else:
                sorted_indices = np.argsort(y)
                shards = np.array_split(sorted_indices, num_clients * 3)
                rng.shuffle(shards)
                for idx, shard in enumerate(shards):
                    client_indices[idx % num_clients].extend(shard)

            for i in range(num_clients):
                client_idx = np.array(client_indices[i], dtype=int)
                rng.shuffle(client_idx)
                clients.append({
                    "client_id": f"hospital_{chr(97 + i)}",
                    "client_name": client_names[i],
                    "X": X[client_idx],
                    "y": y[client_idx],
                    "num_samples": len(client_idx),
                    "partition_strategy": "Non-IID (Skewed Patient Population Distribution)"
                })

        return clients

pipeline = PreprocessingPipeline()

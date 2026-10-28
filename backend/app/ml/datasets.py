import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
from backend.app.config import settings

DATASET_METADATA = {
    "apple_watch": {
        "id": "apple_watch",
        "name": "Harvard Apple Watch & Fitbit Dataset",
        "citation": "Fuller et al. (2020), Harvard Dataverse, DOI: 10.7910/DVN/ZS2Z2J",
        "task": "classification",
        "target_col": "activity",
        "target_description": "Physical activity level (Lying, Sitting, Walking, Running 3/5/7 METs)",
        "file_path": settings.APPLE_WATCH_PATH,
        "default_features": [
            "age", "gender", "height", "weight", "steps", "hear_rate",
            "calories", "distance", "entropy_heart", "entropy_setps",
            "resting_heart", "corr_heart_steps", "norm_heart"
        ]
    },
    "harth": {
        "id": "harth",
        "name": "HARTH Human Activity Recognition Dataset",
        "citation": "Logacjov et al. (2023), UCI Machine Learning Repository, DOI: 10.24432/C5NC90",
        "task": "classification",
        "target_col": "label",
        "target_description": "Annotated activity class (Walking, Running, Standing, Sitting, Lying, Cycling, etc.)",
        "file_path": settings.HARTH_PATH,
        "default_features": ["back_x", "back_y", "back_z", "thigh_x", "thigh_y", "thigh_z"]
    },
    "mi_band": {
        "id": "mi_band",
        "name": "Xiaomi Mi Band Multimodal Activity & Calorie Dataset",
        "citation": "Akhmetov et al. (2025), PeerJ Comput. Sci., DOI: 10.7717/peerj-cs.2870",
        "task": "regression",
        "target_col": "calories",
        "target_description": "Daily calorie expenditure (continuous kcal)",
        "file_path": settings.MI_BAND_PATH,
        "default_features": ["steps", "distance", "runDistance", "deepSleepTime", "shallowSleepTime", "wakeTime"]
    },
    "dat263x": {
        "id": "dat263x",
        "name": "DAT263x Exercise & Calorie Expenditure Dataset",
        "citation": "Mendes (2018), Microsoft / edX DAT263x demos, Kaggle: fmendesdat263xdemos",
        "task": "regression",
        "target_col": "Calories",
        "target_description": "Workout calorie burn (continuous kcal)",
        "file_path": settings.DAT263X_PATH,
        "default_features": ["Gender", "Age", "Height", "Weight", "Duration", "Heart_Rate", "Body_Temp"]
    }
}

class DatasetManager:
    def __init__(self):
        self.cached_dfs: Dict[str, pd.DataFrame] = {}

    def get_dataset_info(self, dataset_id: str) -> Dict[str, Any]:
        meta = DATASET_METADATA.get(dataset_id)
        if not meta:
            raise ValueError(f"Unknown dataset ID: {dataset_id}")
        
        path = Path(meta["file_path"])
        exists = path.exists()
        
        info = {
            "id": meta["id"],
            "name": meta["name"],
            "citation": meta["citation"],
            "task": meta["task"],
            "target_col": meta["target_col"],
            "target_description": meta["target_description"],
            "file_path": str(path),
            "is_available": exists,
            "status": "Available" if exists else "Not available locally",
            "file_size_kb": round(path.stat().st_size / 1024, 2) if exists else 0,
            "features": meta["default_features"]
        }
        
        if exists:
            try:
                df = self.load_dataset(dataset_id)
                info["num_records"] = len(df)
                info["num_features"] = len(df.columns)
                info["missing_values"] = int(df.isnull().sum().sum())
                info["duplicate_rows"] = int(df.duplicated().sum())
                info["columns"] = df.columns.tolist()
                info["dtypes"] = {col: str(dtype) for col, dtype in df.dtypes.items()}
                
                # Target breakdown
                if meta["task"] == "classification":
                    target_counts = df[meta["target_col"]].value_counts().to_dict()
                    info["class_distribution"] = {str(k): int(v) for k, v in target_counts.items()}
                else:
                    info["target_stats"] = {
                        "min": float(df[meta["target_col"]].min()),
                        "max": float(df[meta["target_col"]].max()),
                        "mean": round(float(df[meta["target_col"]].mean()), 2),
                        "std": round(float(df[meta["target_col"]].std()), 2)
                    }
            except Exception as e:
                info["load_error"] = str(e)
                
        return info

    def list_all_datasets(self) -> List[Dict[str, Any]]:
        return [self.get_dataset_info(did) for did in DATASET_METADATA.keys()]

    def load_dataset(self, dataset_id: str) -> pd.DataFrame:
        if dataset_id in self.cached_dfs:
            return self.cached_dfs[dataset_id]
        
        meta = DATASET_METADATA.get(dataset_id)
        if not meta:
            raise ValueError(f"Unknown dataset ID: {dataset_id}")
        
        path = Path(meta["file_path"])
        if not path.exists():
            raise FileNotFoundError(f"Dataset file not found at: {path}")
            
        df = pd.read_csv(path)
        
        # Specific dataset standardizations matching the paper
        if dataset_id == "apple_watch":
            if "device" in df.columns:
                # Optionally filter for Apple Watch records if preferred, or keep all
                pass
            if "Unnamed: 0" in df.columns:
                df = df.drop(columns=["Unnamed: 0"])
        elif dataset_id == "harth":
            if "timestamp" in df.columns:
                df = df.drop(columns=["timestamp"])
                
        self.cached_dfs[dataset_id] = df
        return df

    def get_preview(self, dataset_id: str, limit: int = 10) -> Dict[str, Any]:
        df = self.load_dataset(dataset_id)
        preview_rows = df.head(limit).replace({np.nan: None}).to_dict(orient="records")
        return {
            "dataset_id": dataset_id,
            "total_records": len(df),
            "columns": df.columns.tolist(),
            "preview": preview_rows
        }

dataset_manager = DatasetManager()

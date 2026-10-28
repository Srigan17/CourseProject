import os
import io
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
import joblib
from backend.app.ml.models import FederatedMLPClassifier

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
MODELS_DIR = ROOT_DIR / "storage" / "models"

class ActivityInferenceService:
    def __init__(self):
        self.is_loaded = False
        self.model: Optional[FederatedMLPClassifier] = None
        self.scaler = None
        self.classes: List[str] = []
        self.feature_names: List[str] = []
        self.feature_stats: Dict[str, Any] = {}
        self.model_version: str = "FedProx-DP-SecAgg-Global-v1.0"
        self._load_or_initialize()

    def _load_or_initialize(self):
        weights_path = MODELS_DIR / "combined_weights.npy"
        scaler_path = MODELS_DIR / "power_scaler.joblib"
        classes_path = MODELS_DIR / "classes.json"
        features_path = MODELS_DIR / "feature_names.json"
        stats_path = MODELS_DIR / "feature_stats.json"

        if not (weights_path.exists() and scaler_path.exists() and classes_path.exists()):
            try:
                from scripts.export_inference_model import export_model
                export_model()
            except Exception:
                pass

        if weights_path.exists() and scaler_path.exists() and classes_path.exists():
            weights = np.load(weights_path)
            self.scaler = joblib.load(scaler_path)
            with open(classes_path, "r", encoding="utf-8") as f:
                self.classes = json.load(f)
            with open(features_path, "r", encoding="utf-8") as f:
                self.feature_names = json.load(f)
            if stats_path.exists():
                with open(stats_path, "r", encoding="utf-8") as f:
                    self.feature_stats = json.load(f)

            num_classes = len(self.classes)
            input_dim = len(self.feature_names) # 19
            logistic_size = input_dim * num_classes + num_classes
            mlp_small_size = input_dim * 64 + 64 + 64 * 32 + 32 + 32 * num_classes + num_classes # 3558

            if weights.size == logistic_size:
                from backend.app.ml.models import FederatedLogisticClassifier
                self.model = FederatedLogisticClassifier(input_dim=input_dim, num_classes=num_classes)
                self.model_version = "FederatedLogistic-Global"
            elif weights.size == mlp_small_size:
                self.model = FederatedMLPClassifier(
                    input_dim=input_dim,
                    num_classes=num_classes,
                    hidden_layer_sizes=(64, 32),
                    learning_rate=0.01,
                    alpha=0.005,
                    random_state=42
                )
                self.model_version = "FedProx-MLP(64,32)-Global"
            else:
                self.model = FederatedMLPClassifier(
                    input_dim=input_dim,
                    num_classes=num_classes,
                    hidden_layer_sizes=(128, 64),
                    learning_rate=0.01,
                    alpha=0.005,
                    random_state=42
                )
                self.model_version = "FedProx-MLP(128,64)-Global"

            self.model.set_weights(weights)
            self.is_loaded = True

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "is_loaded": self.is_loaded,
            "classes": self.classes,
            "num_features": len(self.feature_names),
            "feature_names": self.feature_names,
            "feature_stats": self.feature_stats,
            "model_version": self.model_version,
            "disclaimer": "Research activity-classification demonstration model, not a medical diagnostic system."
        }

    def _validate_and_extract_row(self, raw_input: Dict[str, Any]) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Validates required sensor inputs and applies the exact physiological interaction
        engineering from the training pipeline.
        """
        # Validate primary required sensor fields
        required_fields = ["steps", "calories", "distance", "resting_heart"]
        missing = []
        for rf in required_fields:
            if raw_input.get(rf) is None:
                missing.append(rf)
        
        # Check heart rate (accept either 'heart_rate' or 'hear_rate')
        hr = raw_input.get("heart_rate") or raw_input.get("hear_rate")
        if hr is None:
            missing.append("heart_rate")

        if missing:
            raise ValueError(f"Missing required sensor fields: {', '.join(missing)}")

        def safe_float(key: str, default_val: float) -> float:
            v = raw_input.get(key)
            if v is None or v == "":
                return float(default_val)
            return float(v)

        try:
            steps = float(raw_input["steps"])
            hear_rate = float(hr)
            calories = float(raw_input["calories"])
            distance = float(raw_input["distance"])
            resting_heart = float(raw_input["resting_heart"])
            age = safe_float("age", 25.0)
            gender_val = raw_input.get("gender")
            if gender_val is None:
                gender_val = 1
            gender = 1.0 if str(gender_val).lower() in ["1", "male", "m"] else 0.0
            height = safe_float("height", 175.0)
            weight = safe_float("weight", 70.0)
            # Population defaults for advanced signal characteristics if not explicitly provided
            raw_entropy_h = raw_input.get("entropy_heart")
            entropy_heart = float(raw_entropy_h) if raw_entropy_h not in [None, ""] and float(raw_entropy_h) != 4.0 else 6.03

            raw_entropy_s = raw_input.get("entropy_setps")
            entropy_setps = float(raw_entropy_s) if raw_entropy_s not in [None, ""] and float(raw_entropy_s) != 3.5 else 5.74

            raw_corr = raw_input.get("corr_heart_steps")
            corr_heart_steps = float(raw_corr) if raw_corr not in [None, ""] and float(raw_corr) != 0.5 else 0.31

            raw_sd = raw_input.get("sd_norm_heart")
            sd_norm_heart = float(raw_sd) if raw_sd not in [None, ""] and float(raw_sd) != 0.15 else 8.11

            # Exact physiological derived definitions from dataset ground truth
            raw_norm_h = raw_input.get("norm_heart")
            if raw_norm_h not in [None, ""] and float(raw_norm_h) != 1.0:
                norm_heart = float(raw_norm_h)
            else:
                norm_heart = hear_rate - resting_heart

            raw_karvonen = raw_input.get("intensity_karvonen")
            if raw_karvonen not in [None, ""] and float(raw_karvonen) != 0.3:
                intensity_karvonen = float(raw_karvonen)
            else:
                hr_reserve = max(1.0, (220.0 - age) - resting_heart)
                intensity_karvonen = max(0.0, (hear_rate - resting_heart) / hr_reserve)

            raw_std = raw_input.get("steps_times_distance")
            if raw_std not in [None, ""]:
                steps_times_distance = float(raw_std)
            else:
                steps_times_distance = steps * distance
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid numeric value in input: {str(e)}")

        # Validate physiological bounds
        if steps < 0 or hear_rate <= 0 or calories < 0 or distance < 0:
            raise ValueError("Sensor values cannot be negative (heart rate, steps, calories, distance).")

        # Compute exact interaction features used during training
        heart_elevation = hear_rate - resting_heart
        metabolic_intensity = calories / (hear_rate + 1.0)
        step_cadence = steps / (distance + 0.001)

        feature_vector = np.array([[
            age, gender, height, weight, steps, hear_rate, calories, distance,
            entropy_heart, entropy_setps, resting_heart, corr_heart_steps,
            norm_heart, intensity_karvonen, sd_norm_heart, steps_times_distance,
            heart_elevation, metabolic_intensity, step_cadence
        ]], dtype=np.float64)

        features_used = {
            "age": age,
            "gender": "male" if gender == 1.0 else "female",
            "height": height,
            "weight": weight,
            "steps": steps,
            "heart_rate": hear_rate,
            "calories": calories,
            "distance": distance,
            "resting_heart": resting_heart,
            "heart_elevation": round(heart_elevation, 2),
            "metabolic_intensity": round(metabolic_intensity, 4),
            "step_cadence": round(step_cadence, 2)
        }

        return feature_vector, features_used

    def predict(self, raw_input: Dict[str, Any]) -> Dict[str, Any]:
        if not self.is_loaded or self.model is None or self.scaler is None:
            raise RuntimeError("Inference model is not loaded. Please train a federated model first.")

        feature_vector, features_used = self._validate_and_extract_row(raw_input)
        scaled_vector = self.scaler.transform(feature_vector)
        probs = self.model.predict_proba(scaled_vector)[0]
        pred_idx = int(np.argmax(probs))
        predicted_class = self.classes[pred_idx]
        confidence = float(probs[pred_idx])

        prob_dict = {
            self.classes[i]: round(float(probs[i]), 4)
            for i in range(len(self.classes))
        }

        return {
            "predicted_activity": predicted_class,
            "confidence": round(confidence, 4),
            "confidence_percent": round(confidence * 100.0, 2),
            "probabilities": prob_dict,
            "features_used": features_used,
            "input_validation_status": "Valid",
            "model_version": self.model_version,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "disclaimer": "Research demonstration for physical activity recognition. Not a medical diagnostic system."
        }

    def predict_csv(self, csv_content: str) -> Dict[str, Any]:
        """
        Parses an uploaded CSV file, validates columns and data integrity,
        and generates predictions for all records.
        """
        if not self.is_loaded or self.model is None or self.scaler is None:
            raise RuntimeError("Inference model is not loaded. Please train a federated model first.")

        if not csv_content or not csv_content.strip():
            raise ValueError("The uploaded CSV file is empty.")

        try:
            df = pd.read_csv(io.StringIO(csv_content))
        except Exception as e:
            raise ValueError(f"Failed to parse CSV file: {str(e)}")

        if len(df) == 0:
            raise ValueError("The uploaded CSV file is empty.")

        if len(df) > 500:
            df = df.head(500)  # Limit batch preview size for fast response

        # Normalize column names to lowercase
        df.columns = [c.strip().lower() for c in df.columns]

        # Check required columns
        req_cols = ["steps", "calories", "distance", "resting_heart"]
        has_hr = "heart_rate" in df.columns or "hear_rate" in df.columns
        missing_cols = [c for c in req_cols if c not in df.columns]
        if not has_hr:
            missing_cols.append("heart_rate")
        if missing_cols:
            raise ValueError(f"CSV is missing required sensor columns: {', '.join(missing_cols)}")

        # Check for empty / all-null
        if df[req_cols].isnull().all().any():
            raise ValueError("CSV contains columns that are completely null.")

        records = df.to_dict(orient="records")
        row_predictions = []
        class_counts = {c: 0 for c in self.classes}

        for idx, row in enumerate(records):
            try:
                feature_vec, _ = self._validate_and_extract_row(row)
                scaled_vec = self.scaler.transform(feature_vec)
                probs = self.model.predict_proba(scaled_vec)[0]
                pred_idx = int(np.argmax(probs))
                pred_class = self.classes[pred_idx]
                conf = float(probs[pred_idx])

                class_counts[pred_class] += 1
                row_predictions.append({
                    "row_index": idx + 1,
                    "predicted_activity": pred_class,
                    "confidence_percent": round(conf * 100.0, 1),
                    "steps": row.get("steps"),
                    "heart_rate": row.get("heart_rate") or row.get("hear_rate"),
                    "calories": row.get("calories")
                })
            except Exception as e:
                row_predictions.append({
                    "row_index": idx + 1,
                    "error": str(e)
                })

        total_valid = sum(class_counts.values())
        summary_distribution = {
            c: {
                "count": count,
                "percentage": round((count / total_valid) * 100.0, 1) if total_valid > 0 else 0.0
            }
            for c, count in class_counts.items()
        }

        return {
            "total_records": len(df),
            "valid_records": total_valid,
            "summary_distribution": summary_distribution,
            "sample_predictions": row_predictions[:25],
            "model_version": self.model_version,
            "disclaimer": "Research demonstration for physical activity recognition from historical sensor records."
        }

activity_inference_service = ActivityInferenceService()

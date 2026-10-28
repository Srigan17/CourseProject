from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List
from backend.app.ml.datasets import dataset_manager
from backend.app.ml.preprocessing import pipeline

router = APIRouter(prefix="/datasets", tags=["Datasets"])

@router.get("/")
def list_datasets() -> List[Dict[str, Any]]:
    return dataset_manager.list_all_datasets()

@router.get("/{dataset_id}")
def get_dataset(dataset_id: str) -> Dict[str, Any]:
    try:
        return dataset_manager.get_dataset_info(dataset_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{dataset_id}/preview")
def preview_dataset(dataset_id: str, limit: int = Query(10, ge=1, le=100)) -> Dict[str, Any]:
    try:
        return dataset_manager.get_preview(dataset_id, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{dataset_id}/preprocess")
def preprocess_dataset(
    dataset_id: str,
    num_clients: int = Query(3, ge=2, le=8),
    partition_strategy: str = Query("non_iid", pattern="^(iid|non_iid)$"),
    apply_smote: bool = Query(False)
) -> Dict[str, Any]:
    try:
        data = pipeline.prepare_data(
            dataset_id=dataset_id,
            num_clients=num_clients,
            partition_strategy=partition_strategy,
            apply_smote=apply_smote
        )
        return {
            "dataset_id": dataset_id,
            "task": data["task"],
            "train_size": data["train_size"],
            "test_size": data["test_size"],
            "num_features": data["num_features"],
            "feature_names": data["feature_names"],
            "target_classes": data.get("target_classes"),
            "smote_applied": data["smote_applied"],
            "clients": [
                {
                    "client_id": c["client_id"],
                    "client_name": c["client_name"],
                    "num_samples": c["num_samples"],
                    "partition_strategy": c["partition_strategy"]
                }
                for c in data["clients"]
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

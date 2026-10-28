import csv
import io
from fastapi import APIRouter, HTTPException, Response
from typing import Dict, Any, List
from backend.app.ml.experiment_store import experiment_store

router = APIRouter(prefix="/experiments", tags=["Experiments"])

@router.get("/")
def list_experiments() -> List[Dict[str, Any]]:
    return experiment_store.list_experiments()

@router.get("/controlled-study")
def get_controlled_study_results():
    from pathlib import Path
    p = Path(__file__).resolve().parent.parent.parent.parent / "storage" / "experiments" / "controlled_experiments_results.json"
    if p.exists():
        return Response(content=p.read_text(encoding="utf-8"), media_type="application/json")
    return Response(content='{"status": "not_executed"}', media_type="application/json")

@router.get("/{exp_id}")
def get_experiment(exp_id: str) -> Dict[str, Any]:
    exp = experiment_store.get_experiment(exp_id)
    if not exp:
        raise HTTPException(status_code=404, detail=f"Experiment '{exp_id}' not found.")
    return exp

@router.delete("/{exp_id}")
def delete_experiment(exp_id: str):
    success = experiment_store.delete_experiment(exp_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Experiment '{exp_id}' not found.")
    return {"message": f"Experiment '{exp_id}' deleted."}

@router.get("/export/csv")
def export_experiments_csv():
    experiments = experiment_store.list_experiments()
    output = io.StringIO()
    writer = csv.writer(output)
    
    headers = [
        "Experiment ID", "Mode", "Dataset", "Task", "Rounds/Epochs",
        "DP Enabled", "SecAgg Enabled", "Accuracy / RMSE", "F1 / MAE",
        "Time (s)", "Comm Cost (KB)", "Created At"
    ]
    writer.writerow(headers)

    for e in experiments:
        metrics = e.get("metrics", {})
        acc_rmse = metrics.get("accuracy", metrics.get("rmse", "N/A"))
        f1_mae = metrics.get("f1_score", metrics.get("mae", "N/A"))
        writer.writerow([
            e.get("id"),
            e.get("experiment_mode"),
            e.get("dataset_id"),
            e.get("task"),
            e.get("rounds_completed", e.get("epochs", "N/A")),
            e.get("differential_privacy_enabled", False),
            e.get("secure_aggregation_enabled", False),
            acc_rmse,
            f1_mae,
            e.get("elapsed_time_sec"),
            e.get("communication_cost_kb"),
            e.get("created_at")
        ])

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=experiments_summary.csv"}
    )

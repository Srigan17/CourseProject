import os
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
from backend.app.config import settings

class ExperimentStore:
    def __init__(self, storage_dir: Path = settings.EXPERIMENTS_DIR):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        self.index_file = self.storage_dir / "index.json"
        self._experiments: Dict[str, Dict[str, Any]] = {}
        self._load_index()

    def _load_index(self):
        if self.index_file.exists():
            try:
                with open(self.index_file, "r", encoding="utf-8") as f:
                    self._experiments = json.load(f)
            except Exception:
                self._experiments = {}

    def _save_index(self):
        try:
            with open(self.index_file, "w", encoding="utf-8") as f:
                json.dump(self._experiments, f, indent=2)
        except Exception:
            pass

    def save_experiment(self, exp_data: Dict[str, Any]) -> str:
        exp_id = str(uuid.uuid4())[:8]
        exp_data["id"] = exp_id
        exp_data["created_at"] = datetime.now(timezone.utc).isoformat()
        
        self._experiments[exp_id] = exp_data
        self._save_index()

        # Also write individual json file
        exp_file = self.storage_dir / f"exp_{exp_id}.json"
        with open(exp_file, "w", encoding="utf-8") as f:
            json.dump(exp_data, f, indent=2)

        return exp_id

    def get_experiment(self, exp_id: str) -> Optional[Dict[str, Any]]:
        return self._experiments.get(exp_id)

    def list_experiments(self) -> List[Dict[str, Any]]:
        # Newest first
        return sorted(list(self._experiments.values()), key=lambda x: x.get("created_at", ""), reverse=True)

    def delete_experiment(self, exp_id: str) -> bool:
        if exp_id in self._experiments:
            del self._experiments[exp_id]
            self._save_index()
            f = self.storage_dir / f"exp_{exp_id}.json"
            if f.exists():
                f.unlink()
            return True
        return False

experiment_store = ExperimentStore()

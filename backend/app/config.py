import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"

class Settings(BaseModel):
    PROJECT_NAME: str = "Privacy-Preserving Healthcare Federated Learning Platform"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Security Secrets (can be overridden via environment variables)
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "f7b8c8d2348a471e98a129ef3b8891ac410947c92019b88cf1e857412e84cba3")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # AES-256-GCM Encryption key at rest (must be 32 bytes hex)
    AES_GCM_KEY_HEX: str = os.getenv("AES_GCM_KEY_HEX", "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef")
    
    # Paths
    APPLE_WATCH_PATH: Path = DATA_DIR / "apple_watch" / "aw_fb_data.csv"
    HARTH_PATH: Path = DATA_DIR / "harth" / "harth_110k.csv"
    MI_BAND_PATH: Path = DATA_DIR / "mi_band" / "mi_band_merged.csv"
    DAT263X_PATH: Path = DATA_DIR / "dat263x" / "dat263x_merged.csv"
    
    STORAGE_DIR: Path = BASE_DIR / "storage"
    AUDIT_LOG_FILE: Path = BASE_DIR / "storage" / "audit_events.jsonl"
    EXPERIMENTS_DIR: Path = BASE_DIR / "storage" / "experiments"
    MODELS_DIR: Path = BASE_DIR / "storage" / "models"
    
    # Paillier Key Length (512 for fast responsive interactive runs, 1024 or 2048 for high security)
    PAILLIER_KEY_LENGTH: int = int(os.getenv("PAILLIER_KEY_LENGTH", "512"))

settings = Settings()
os.makedirs(settings.STORAGE_DIR, exist_ok=True)
os.makedirs(settings.EXPERIMENTS_DIR, exist_ok=True)
os.makedirs(settings.MODELS_DIR, exist_ok=True)

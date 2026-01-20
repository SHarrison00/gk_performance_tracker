from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parents[1]  # .../gk_performance_tracker/app
PROJECT_DIR = BASE_DIR.parent                   # .../gk_performance_tracker/gk_performance_tracker

@dataclass(frozen=True)
class Config:
    """
    Central application configuration.
    """
    # Local data directory
    DATA_DIR: Path = (PROJECT_DIR / os.getenv("DATA_DIR", "app/data/raw")).resolve()
    
    # Min time between S3 sync attempts
    MIN_SYNC_INTERVAL_SECONDS: int = int(os.getenv("MIN_SYNC_INTERVAL_SECONDS", 300))
    
    # AWS
    S3_BUCKET: str = os.getenv("S3_BUCKET", "gk-performance-tracker-data")
    S3_PREFIX: str = os.getenv("S3_PREFIX", "latest")

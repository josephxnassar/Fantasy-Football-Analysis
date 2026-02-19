"""Application settings loaded from environment variables"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root (two levels up from this file)
_project_root = Path(__file__).resolve().parent.parent.parent
load_dotenv(_project_root / ".env")

# API
API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
API_PORT: int = int(os.getenv("API_PORT", "8000"))

# CORS - comma-separated origins, or "*" for dev
_raw_cors_origins = os.getenv("CORS_ORIGINS", "*").strip()
if _raw_cors_origins == "*":
    CORS_ORIGINS: list[str] = ["*"]
else:
    CORS_ORIGINS = [origin.strip() for origin in _raw_cors_origins.split(",") if origin.strip()]

CORS_ALLOW_CREDENTIALS: bool = (os.getenv("CORS_ALLOW_CREDENTIALS", "false").strip().lower() in {"1", "true", "yes", "on"})

# Database
DB_PATH: str = os.getenv("DB_PATH", "backend/database/data/nfl_cache.db")

# Logging
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "DEBUG").upper()
LOG_CONSOLE_LEVEL: str = os.getenv("LOG_CONSOLE_LEVEL", "INFO").upper()
LOG_DIR: str = os.getenv("LOG_DIR", "logs")
LOG_ROTATION_WHEN: str = os.getenv("LOG_ROTATION_WHEN", "midnight")
LOG_ROTATION_INTERVAL: int = int(os.getenv("LOG_ROTATION_INTERVAL", "1"))
LOG_BACKUP_COUNT: int = int(os.getenv("LOG_BACKUP_COUNT", "14"))
TIMING_ENABLED: bool = os.getenv("TIMING_ENABLED", "false").strip().lower() in {"1", "true", "yes", "on"}

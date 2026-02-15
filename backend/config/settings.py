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
CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "*").split(",")

# Database
DB_PATH: str = os.getenv("DB_PATH", "backend/database/data/nfl_cache.db")

# Logging
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "DEBUG").upper()

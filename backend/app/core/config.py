"""
PolyShift - Core Configuration Module
"""
import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent
WORKSPACE_DIR = BASE_DIR.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

class Settings(BaseModel):
    PROJECT_NAME: str = "PolyShift — Universal Code Translation Engine"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'polyshift.db'}")
    
    # Sandboxing & Execution Limits
    EXECUTION_TIMEOUT_SECONDS: int = int(os.getenv("EXECUTION_TIMEOUT_SECONDS", "5"))
    MAX_CODE_SIZE_BYTES: int = int(os.getenv("MAX_CODE_SIZE_BYTES", "1048576"))  # 1 MB
    MAX_OUTPUT_BYTES: int = int(os.getenv("MAX_OUTPUT_BYTES", "65536"))  # 64 KB
    
    # Optional AI Settings
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    AI_MODEL_GEMINI: str = os.getenv("AI_MODEL_GEMINI", "gemini-2.5-flash")
    AI_MODEL_OPENAI: str = os.getenv("AI_MODEL_OPENAI", "gpt-4o-mini")
    
    # CORS
    CORS_ORIGINS: list[str] = ["*"]

settings = Settings()


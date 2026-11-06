"""
PolyShift - System Health & Diagnostics Route
"""
import shutil
import platform
import os
from fastapi import APIRouter
from app.core.config import settings
from app.engines.ai.provider import ai_provider

router = APIRouter()

@router.get("/health")
def health_check():
    compilers = {
        "python": shutil.which("python3") or shutil.which("python"),
        "node": shutil.which("node"),
        "cpp": shutil.which("g++") or shutil.which("clang++"),
        "rustc": shutil.which("rustc")
    }

    return {
        "status": "healthy",
        "app_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "compilers_detected": compilers,
        "ai_integration": ai_provider.get_status()
    }


"""
PolyShift — Universal Code Translation Engine
Main FastAPI Application Entrypoint
"""
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.database.db import init_db

# Import routers
from app.api.routes.translate import router as translate_router
from app.api.routes.analyze import router as analyze_router
from app.api.routes.explain import router as explain_router
from app.api.routes.optimize import router as optimize_router
from app.api.routes.compare import router as compare_router
from app.api.routes.validate import router as validate_router
from app.api.routes.execute import router as execute_router
from app.api.routes.history import router as history_router
from app.api.routes.examples import router as examples_router
from app.api.routes.health import router as health_router
from app.api.routes.stats import router as stats_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database Tables
    init_db()
    yield
    # Shutdown logic if any

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Universal code translation and intelligence engine across Python, C++, JavaScript, and Rust.",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 Routes
api_v1 = settings.API_V1_STR
app.include_router(translate_router, prefix=api_v1, tags=["Translation"])
app.include_router(analyze_router, prefix=api_v1, tags=["Analysis"])
app.include_router(explain_router, prefix=api_v1, tags=["Explainer"])
app.include_router(optimize_router, prefix=api_v1, tags=["Optimization"])
app.include_router(compare_router, prefix=api_v1, tags=["Comparison"])
app.include_router(validate_router, prefix=api_v1, tags=["Validation"])
app.include_router(execute_router, prefix=api_v1, tags=["Execution"])
app.include_router(history_router, prefix=api_v1, tags=["History"])
app.include_router(examples_router, prefix=api_v1, tags=["Examples"])
app.include_router(health_router, prefix=api_v1, tags=["Health"])
app.include_router(stats_router, prefix=api_v1, tags=["Statistics"])

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred in PolyShift Engine.", "error": str(exc)}
    )

# Static Frontend mounting
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        index_file = FRONTEND_DIR / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"message": "PolyShift API is running. Frontend index.html not found."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)


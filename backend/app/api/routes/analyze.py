"""
PolyShift - Code Analysis Route
"""
from fastapi import APIRouter, HTTPException
from app.models.schemas import AnalyzeRequest, AnalyzeResponse
from app.engines.analyzer import analyze_code_metrics

router = APIRouter()

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_code(req: AnalyzeRequest):
    if not req.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty.")
    
    metrics = analyze_code_metrics(req.code, req.language)
    return AnalyzeResponse(**metrics)

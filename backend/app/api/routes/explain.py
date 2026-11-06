"""
PolyShift - Code Explanation Route
"""
from fastapi import APIRouter, HTTPException
from app.models.schemas import ExplainRequest, ExplainResponse
from app.engines.explainer import explain_code

router = APIRouter()

@router.post("/explain", response_model=ExplainResponse)
async def explain(req: ExplainRequest):
    if not req.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty.")
    
    explanation = explain_code(req.code, req.language, req.level)
    return ExplainResponse(**explanation)


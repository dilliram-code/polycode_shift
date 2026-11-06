"""
PolyShift - Code Optimization Route
"""
from fastapi import APIRouter, HTTPException
from app.models.schemas import OptimizeRequest, OptimizeResponse
from app.engines.optimizer import optimize_code

router = APIRouter()

@router.post("/optimize", response_model=OptimizeResponse)
async def optimize(req: OptimizeRequest):
    if not req.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty.")
    
    result = optimize_code(req.code, req.language)
    return OptimizeResponse(**result)

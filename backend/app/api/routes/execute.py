"""
PolyShift - Sandboxed Execution Route
"""
from fastapi import APIRouter
from app.models.schemas import ExecuteRequest, ExecuteResponse
from app.engines.validator import execute_code

router = APIRouter()

@router.post("/execute", response_model=ExecuteResponse)
async def execute(req: ExecuteRequest):
    result = execute_code(req.code, req.language)
    return ExecuteResponse(**result)

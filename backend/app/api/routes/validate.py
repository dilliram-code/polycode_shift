"""
PolyShift - Code Validation Route
"""
from fastapi import APIRouter
from app.models.schemas import ValidateRequest, ValidateResponse
from app.engines.validator import validate_code

router = APIRouter()

@router.post("/validate", response_model=ValidateResponse)
async def validate(req: ValidateRequest):
    result = validate_code(req.code, req.language)
    return ValidateResponse(**result)


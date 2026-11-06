"""
PolyShift - Code Comparison Route
"""
from fastapi import APIRouter, HTTPException
from app.models.schemas import CompareRequest, CompareResponse
from app.engines.comparator import compare_code_snippets

router = APIRouter()

@router.post("/compare", response_model=CompareResponse)
async def compare(req: CompareRequest):
    result = compare_code_snippets(
        req.source_code,
        req.target_code,
        req.source_language,
        req.target_language
    )
    return CompareResponse(**result)

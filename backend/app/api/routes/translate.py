"""
PolyShift - Translation Route
"""
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.models import TranslationHistory
from app.models.schemas import TranslationRequest, TranslationResponse
from app.engines.translators.translator import translator_engine
from app.engines.ai.provider import ai_provider

router = APIRouter()

@router.post("/translate", response_model=TranslationResponse)
async def translate_code(req: TranslationRequest, db: Session = Depends(get_db)):
    if not req.source_code.strip():
        raise HTTPException(status_code=400, detail="Source code cannot be empty.")

    # Execute deterministic translation
    result = translator_engine.translate(
        source_code=req.source_code,
        source_language=req.source_language,
        target_language=req.target_language
    )

    translated_code = result["translated_code"]

    # Optional AI assistance if requested and available
    if req.use_ai and ai_provider.is_available():
        ai_res = await ai_provider.assist_translation(
            req.source_code,
            result["source_language"],
            result["target_language"]
        )
        if ai_res:
            translated_code = ai_res
            result["status"] = "success (ai-assisted)"

    # Persist in SQLite history
    history_record = TranslationHistory(
        source_language=result["source_language"],
        target_language=result["target_language"],
        source_code=req.source_code,
        target_code=translated_code,
        translation_status=result["status"],
        confidence_score=result["confidence"],
        warnings_json=json.dumps(result["warnings"]),
        title=req.title or f"{result['source_language'].title()} to {result['target_language'].title()} Translation"
    )
    db.add(history_record)
    db.commit()
    db.refresh(history_record)

    return TranslationResponse(
        success=result["success"],
        source_language=result["source_language"],
        target_language=result["target_language"],
        detected_language=result["detected_language"],
        source_code=req.source_code,
        translated_code=translated_code,
        status=result["status"],
        confidence=result["confidence"],
        warnings=result["warnings"],
        semantic_differences=result["semantic_differences"],
        approximation_notices=result["approximation_notices"],
        ast_summary=result["ast_summary"],
        history_id=history_record.id
    )


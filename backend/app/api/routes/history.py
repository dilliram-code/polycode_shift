"""
PolyShift - Translation History Route
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
import json
import csv
import io

from app.database.db import get_db
from app.database.models import TranslationHistory
from app.models.schemas import HistoryItemResponse

router = APIRouter()

@router.get("/history", response_model=List[HistoryItemResponse])
def get_history(
    q: Optional[str] = Query(None, description="Search keyword in code or title"),
    source_lang: Optional[str] = Query(None),
    target_lang: Optional[str] = Query(None),
    bookmarked_only: bool = Query(False),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db)
):
    query = db.query(TranslationHistory)
    if bookmarked_only:
        query = query.filter(TranslationHistory.is_bookmarked == True)
    if source_lang:
        query = query.filter(TranslationHistory.source_language == source_lang.lower())
    if target_lang:
        query = query.filter(TranslationHistory.target_language == target_lang.lower())
    if q:
        search_filter = f"%{q}%"
        query = query.filter(
            (TranslationHistory.title.ilike(search_filter)) |
            (TranslationHistory.source_code.ilike(search_filter)) |
            (TranslationHistory.target_code.ilike(search_filter))
        )

    records = query.order_by(TranslationHistory.created_at.desc()).limit(limit).all()

    return [
        HistoryItemResponse(
            id=r.id,
            source_language=r.source_language,
            target_language=r.target_language,
            source_code=r.source_code,
            target_code=r.target_code,
            translation_status=r.translation_status,
            confidence_score=r.confidence_score,
            created_at=r.created_at.isoformat(),
            is_bookmarked=r.is_bookmarked,
            title=r.title
        )
        for r in records
    ]

@router.delete("/history/{record_id}")
def delete_history_item(record_id: int, db: Session = Depends(get_db)):
    record = db.query(TranslationHistory).filter(TranslationHistory.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="History record not found.")
    db.delete(record)
    db.commit()
    return {"message": "Record deleted successfully.", "id": record_id}

@router.post("/history/{record_id}/bookmark")
def toggle_bookmark(record_id: int, db: Session = Depends(get_db)):
    record = db.query(TranslationHistory).filter(TranslationHistory.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="History record not found.")
    record.is_bookmarked = not record.is_bookmarked
    db.commit()
    return {"id": record.id, "is_bookmarked": record.is_bookmarked}

@router.get("/history/export")
def export_history(format: str = Query("json", pattern="^(json|csv)$"), db: Session = Depends(get_db)):
    records = db.query(TranslationHistory).order_by(TranslationHistory.created_at.desc()).all()
    if format == "json":
        data = [
            {
                "id": r.id,
                "source_language": r.source_language,
                "target_language": r.target_language,
                "source_code": r.source_code,
                "target_code": r.target_code,
                "translation_status": r.translation_status,
                "confidence_score": r.confidence_score,
                "created_at": r.created_at.isoformat(),
                "title": r.title
            }
            for r in records
        ]
        return Response(
            content=json.dumps(data, indent=2),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=polyshift_history.json"}
        )
    else:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Source Lang", "Target Lang", "Status", "Confidence", "Created At", "Title"])
        for r in records:
            writer.writerow([r.id, r.source_language, r.target_language, r.translation_status, r.confidence_score, r.created_at.isoformat(), r.title])
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=polyshift_history.csv"}
        )

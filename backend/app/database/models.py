"""
PolyShift - Database Models
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean
from app.database.db import Base

class TranslationHistory(Base):
    __tablename__ = "translation_history"

    id = Column(Integer, primary_key=True, index=True)
    source_language = Column(String(50), nullable=False, index=True)
    target_language = Column(String(50), nullable=False, index=True)
    source_code = Column(Text, nullable=False)
    target_code = Column(Text, nullable=False)
    translation_status = Column(String(50), default="success") # success, warning, approx
    confidence_score = Column(Float, default=1.0)
    warnings_json = Column(Text, nullable=True) # JSON list
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    is_bookmarked = Column(Boolean, default=False)
    title = Column(String(200), nullable=True)

class ExampleItem(Base):
    __tablename__ = "example_items"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(100), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    python_code = Column(Text, nullable=False)
    cpp_code = Column(Text, nullable=False)
    javascript_code = Column(Text, nullable=False)
    rust_code = Column(Text, nullable=False)
    difficulty = Column(String(50), default="intermediate")

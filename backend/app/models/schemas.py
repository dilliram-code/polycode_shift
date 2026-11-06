"""
PolyShift - API Request and Response Pydantic Schemas
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# --- Translation ---

class TranslationRequest(BaseModel):
    source_code: str = Field(..., description="Source code to translate", max_length=1048576)
    source_language: str = Field(..., description="Source language ('python', 'cpp', 'javascript', 'rust', or 'auto')")
    target_language: str = Field(..., description="Target language ('python', 'cpp', 'javascript', 'rust')")
    use_ai: Optional[bool] = Field(False, description="Attempt AI assistance if available")
    title: Optional[str] = Field(None, description="Optional title for history")

class TranslationResponse(BaseModel):
    success: bool
    source_language: str
    target_language: str
    detected_language: str
    source_code: str
    translated_code: str
    status: str  # success, warning, approximate, error
    confidence: float
    warnings: List[str]
    semantic_differences: List[str]
    approximation_notices: List[str]
    ast_summary: Dict[str, Any]
    history_id: Optional[int] = None

# --- Analysis ---

class AnalyzeRequest(BaseModel):
    code: str = Field(..., max_length=1048576)
    language: str

class AnalyzeResponse(BaseModel):
    loc: int
    code_lines: int
    blank_lines: int
    comment_lines: int
    function_count: int
    class_count: int
    loop_count: int
    conditional_count: int
    variable_count: int
    return_count: int
    cyclomatic_complexity: int
    nesting_depth: int
    complexity_rating: str
    diagnostics: List[str]

# --- Explanation ---

class ExplainRequest(BaseModel):
    code: str = Field(..., max_length=1048576)
    language: str
    level: str = Field("intermediate", description="beginner, intermediate, advanced")

class ExplainResponse(BaseModel):
    level: str
    language: str
    executive_summary: str
    time_complexity: str
    space_complexity: str
    functions_detected: List[str]
    algorithmic_steps: List[Dict[str, str]]
    language_idioms: List[str]

# --- Optimization ---

class OptimizeRequest(BaseModel):
    code: str = Field(..., max_length=1048576)
    language: str

class OptimizeResponse(BaseModel):
    language: str
    optimizations_count: int
    optimizations: List[Dict[str, str]]
    original_code: str
    suggested_code: str

# --- Comparison ---

class CompareRequest(BaseModel):
    source_code: str = Field(..., max_length=1048576)
    target_code: str = Field(..., max_length=1048576)
    source_language: str
    target_language: str

class CompareResponse(BaseModel):
    source_language: str
    target_language: str
    similarity_ratio: float
    added_lines: int
    removed_lines: int
    modified_lines: int
    total_source_lines: int
    total_target_lines: int
    unified_diff: str
    construct_mappings: List[Dict[str, str]]

# --- Validation and Execution ---

class ValidateRequest(BaseModel):
    code: str = Field(..., max_length=1048576)
    language: str

class ValidateResponse(BaseModel):
    valid: bool
    stage: str
    errors: List[str]
    compiler_available: bool
    compiler_info: str

class ExecuteRequest(BaseModel):
    code: str = Field(..., max_length=1048576)
    language: str
    timeout: Optional[int] = Field(5, le=30)

class ExecuteResponse(BaseModel):
    success: bool
    stdout: str
    stderr: str
    exit_code: int
    execution_time_ms: float
    validation_status: str
    error: Optional[str] = None

# --- History & Examples ---

class HistoryItemResponse(BaseModel):
    id: int
    source_language: str
    target_language: str
    source_code: str
    target_code: str
    translation_status: str
    confidence_score: float
    created_at: str
    is_bookmarked: bool
    title: Optional[str] = None

class ExampleResponse(BaseModel):
    id: int
    category: str
    title: str
    description: Optional[str] = None
    python_code: str
    cpp_code: str
    javascript_code: str
    rust_code: str
    difficulty: str


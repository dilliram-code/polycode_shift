"""
PolyShift - Code Validation Engine
Performs multi-stage code validation: syntax checking, compilation test, and sandboxed execution.
"""
from typing import Dict, Any
from app.engines.parsers.python_parser import PythonParser
from app.engines.parsers.javascript_parser import JavaScriptParser
from app.engines.parsers.cpp_parser import CppParser
from app.engines.parsers.rust_parser import RustParser
from app.core.security import run_sandboxed_code, check_compiler_availability

parsers = {
    "python": PythonParser(),
    "javascript": JavaScriptParser(),
    "cpp": CppParser(),
    "rust": RustParser()
}

def validate_code(code: str, language: str) -> Dict[str, Any]:
    """
    Validates code syntax and verifies compiler availability.
    """
    lang = language.lower()
    if lang not in parsers:
        return {
            "valid": False,
            "stage": "unsupported_language",
            "errors": [f"Language '{language}' is not supported for validation."],
            "compiler_available": False,
            "compiler_info": ""
        }

    parser = parsers[lang]
    is_valid_syntax, syntax_errors = parser.validate_syntax(code)
    is_compiler_avail, compiler_info = check_compiler_availability(lang)

    return {
        "valid": is_valid_syntax,
        "stage": "syntax_analysis",
        "errors": syntax_errors,
        "compiler_available": is_compiler_avail,
        "compiler_info": compiler_info
    }

def execute_code(code: str, language: str) -> Dict[str, Any]:
    """
    Executes code in an isolated sandboxed subprocess with execution limits.
    """
    return run_sandboxed_code(code, language)

"""
PolyShift - Universal Bidirectional Translation Engine
Coordinates parsing, semantic analysis, intermediate representation mapping,
code generation, and diagnostic reporting for all 12 language pairs.
"""
from typing import Dict, Any, List, Optional, Tuple

from app.engines.parsers.detector import detect_language
from app.engines.parsers.python_parser import PythonParser
from app.engines.parsers.javascript_parser import JavaScriptParser
from app.engines.parsers.cpp_parser import CppParser
from app.engines.parsers.rust_parser import RustParser

from app.engines.generators.python_generator import PythonGenerator
from app.engines.generators.javascript_generator import JavaScriptGenerator
from app.engines.generators.cpp_generator import CppGenerator
from app.engines.generators.rust_generator import RustGenerator

# Semantic notes and potential caveats for each language pair
PAIR_SEMANTICS: Dict[Tuple[str, str], Dict[str, Any]] = {
    ("python", "cpp"): {
        "notes": [
            "Python dynamic typing mapped to C++ static types (defaulting to auto or inferred container types).",
            "Python garbage collection replaced by C++ RAII (automatic stack storage and std::vector memory).",
            "print() statements mapped to std::cout with std::endl."
        ],
        "warnings": [
            "Heterogeneous collections in Python (e.g. [1, 'two']) will default to std::vector<int> unless manually adapted.",
            "Dynamic attribute additions to objects at runtime are not permitted in C++."
        ]
    },
    ("python", "javascript"): {
        "notes": [
            "Python indentation converted to JavaScript curly braces and semicolons.",
            "print() translated to console.log().",
            "Python None and booleans converted to null, true, false."
        ],
        "warnings": [
            "Python integer division '//' requires Math.floor() in JavaScript if floating results are not desired.",
            "Python dict keys can be tuples or objects; JS object keys are strings or Symbols."
        ]
    },
    ("python", "rust"): {
        "notes": [
            "Python variables converted to Rust `let mut` declarations.",
            "Lists translated to Rust `Vec<T>` and strings to `String`.",
            "Top-level code wrapped in `fn main()`."
        ],
        "warnings": [
            "Rust requires strict ownership and borrow checking; cloned values may be required for shared references.",
            "Rust does not have Python's None for all types; Option<T> is used when nullability is needed."
        ]
    },
    ("cpp", "python"): {
        "notes": [
            "C++ type declarations stripped to idiomatic Python dynamic variables.",
            "std::vector and std::string converted to native Python lists and str.",
            "std::cout translated to print()."
        ],
        "warnings": [
            "C++ pointer arithmetic and raw memory access cannot be directly translated without ctypes/struct.",
            "C++ template metaprogramming converted to standard polymorphic Python functions."
        ]
    },
    ("cpp", "javascript"): {
        "notes": [
            "C++ types replaced with let/const.",
            "std::cout translated to console.log.",
            "std::vector methods mapped to JavaScript Array methods."
        ],
        "warnings": [
            "C++ integer overflows wrap based on bit-width, whereas JavaScript numbers are 64-bit floats.",
            "C++ destructors and deterministic RAII cleanup must be handled manually or by Garbage Collection."
        ]
    },
    ("cpp", "rust"): {
        "notes": [
            "C++ types mapped to Rust equivalents (int -> i32, double -> f64, std::vector -> Vec).",
            "Classes and methods mapped to Rust structs and impl blocks.",
            "std::cout replaced with println!()."
        ],
        "warnings": [
            "Unrestricted C++ pointer references must conform to Rust's borrow checker rules.",
            "C++ inheritance hierarchies must be refactored into Rust traits and composition."
        ]
    },
    ("javascript", "python"): {
        "notes": [
            "JS const/let converted to Python variables.",
            "console.log() translated to print().",
            "JS null/undefined mapped to Python None."
        ],
        "warnings": [
            "JavaScript truthiness (e.g. '0' is true, [] is true) differs from Python (0 is False, [] is False).",
            "Asynchronous Promises require asyncio/await in Python."
        ]
    },
    ("javascript", "cpp"): {
        "notes": [
            "JS variables mapped to C++ typed variables with auto or explicit types.",
            "console.log() converted to std::cout.",
            "Arrays mapped to std::vector."
        ],
        "warnings": [
            "JavaScript dynamic object properties require std::map or custom structs in C++.",
            "JavaScript loose equality '==' behaviors are not replicated in C++ strict comparisons."
        ]
    },
    ("javascript", "rust"): {
        "notes": [
            "JS let/const converted to Rust `let mut` and `let`.",
            "console.log() converted to println!().",
            "Arrays mapped to Vec<T>."
        ],
        "warnings": [
            "JavaScript closure capturing by reference requires explicit Rust ownership moves or Arc<Mutex<T>>.",
            "Dynamic property access requires Rust serde_json::Value or HashMap."
        ]
    },
    ("rust", "python"): {
        "notes": [
            "Rust explicit types and mutability stripped to Python dynamic variables.",
            "println!() converted to print().",
            "Vec<T> mapped to Python list."
        ],
        "warnings": [
            "Rust Result/Option handling unwrapped or mapped to Python exceptions.",
            "Rust thread safety guarantees and compile-time race condition checks do not apply in Python."
        ]
    },
    ("rust", "cpp"): {
        "notes": [
            "Rust types mapped to C++ (i32 -> int, f64 -> double, Vec -> std::vector, String -> std::string).",
            "println!() converted to std::cout.",
            "Structs and impls merged into C++ classes."
        ],
        "warnings": [
            "Rust enum with data (tagged unions) mapped to std::variant or polymorphic classes.",
            "Rust pattern matching mapped to if-else or switch constructs."
        ]
    },
    ("rust", "javascript"): {
        "notes": [
            "Rust let mut converted to let, let converted to const.",
            "println!() converted to console.log().",
            "Vec mapped to Array."
        ],
        "warnings": [
            "Rust 64-bit unsigned integers (u64) beyond 2^53 - 1 require BigInt in JavaScript.",
            "Rust memory safety is replaced by V8 engine garbage collection."
        ]
    }
}

class TranslationEngine:
    def __init__(self):
        self.parsers = {
            "python": PythonParser(),
            "javascript": JavaScriptParser(),
            "cpp": CppParser(),
            "rust": RustParser()
        }
        self.generators = {
            "python": PythonGenerator(),
            "javascript": JavaScriptGenerator(),
            "cpp": CppGenerator(),
            "rust": RustGenerator()
        }

    def translate(
        self,
        source_code: str,
        source_language: str,
        target_language: str
    ) -> Dict[str, Any]:
        """
        Executes end-to-end translation between any supported language pair.
        Returns detailed report with translated code, diagnostics, warnings, and confidence.
        """
        src_lang = source_language.lower().strip()
        tgt_lang = target_language.lower().strip()

        # Handle auto-detection
        detected_lang = None
        detect_confidence = 1.0
        if src_lang == "auto" or src_lang not in self.parsers:
            detected_lang, detect_confidence = detect_language(source_code)
            src_lang = detected_lang

        if src_lang not in self.parsers:
            return {
                "success": False,
                "translated_code": "",
                "source_language": src_lang,
                "target_language": tgt_lang,
                "detected_language": detected_lang or src_lang,
                "status": "error",
                "confidence": 0.0,
                "warnings": [f"Unsupported source language: {source_language}"],
                "semantic_differences": [],
                "approximation_notices": [],
                "ast_summary": {}
            }

        if tgt_lang not in self.generators:
            return {
                "success": False,
                "translated_code": "",
                "source_language": src_lang,
                "target_language": tgt_lang,
                "detected_language": detected_lang or src_lang,
                "status": "error",
                "confidence": 0.0,
                "warnings": [f"Unsupported target language: {target_language}"],
                "semantic_differences": [],
                "approximation_notices": [],
                "ast_summary": {}
            }

        # 1. Parse source code into IR
        parser = self.parsers[src_lang]
        is_valid_syntax, syntax_errors = parser.validate_syntax(source_code)
        
        warnings: List[str] = []
        approximations: List[str] = []

        if not is_valid_syntax and syntax_errors:
            warnings.extend([f"Syntax Notice: {err}" for err in syntax_errors[:3]])

        ir_program = parser.parse(source_code)

        # 2. Generate target code from IR
        generator = self.generators[tgt_lang]
        translated_code = generator.generate(ir_program)

        # 3. Compute semantic differences and warnings
        pair_info = PAIR_SEMANTICS.get((src_lang, tgt_lang), {
            "notes": [f"Direct AST and semantic mapping between {src_lang.title()} and {tgt_lang.title()}."],
            "warnings": []
        })

        semantic_differences = pair_info.get("notes", [])
        warnings.extend(pair_info.get("warnings", []))

        # Check for approximations
        if src_lang == "python" and tgt_lang in ("cpp", "rust"):
            approximations.append("Dynamic types in Python were mapped to inferred static types.")
        if src_lang in ("cpp", "rust") and tgt_lang == "python":
            approximations.append("Static type declarations were transformed into Python dynamically typed bindings.")

        # 4. Compute confidence score
        # Base confidence starts at 0.95 for direct IR mapping
        confidence = 0.95
        if not is_valid_syntax:
            confidence -= 0.20
        if len(warnings) > 1:
            confidence -= 0.05 * min(len(warnings), 3)
        confidence = max(0.40, min(0.98, round(confidence, 2)))

        status = "success"
        if not is_valid_syntax:
            status = "approximate"
        elif len(warnings) > 0:
            status = "warning"

        ast_summary = {
            "functions_count": len(ir_program.functions),
            "classes_count": len(ir_program.classes),
            "statements_count": len(ir_program.statements),
            "imports_count": len(ir_program.imports)
        }

        return {
            "success": True,
            "translated_code": translated_code,
            "source_language": src_lang,
            "target_language": tgt_lang,
            "detected_language": detected_lang or src_lang,
            "status": status,
            "confidence": confidence,
            "warnings": warnings,
            "semantic_differences": semantic_differences,
            "approximation_notices": approximations,
            "ast_summary": ast_summary
        }

# Global singleton
translator_engine = TranslationEngine()


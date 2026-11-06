"""
PolyShift - Code Explanation Engine
Generates multi-tier explanations (Beginner, Intermediate, Advanced)
covering logic, algorithms, control flow, time/space complexity, and idioms.
"""
import re
from typing import Dict, Any, List

def explain_code(code: str, language: str, level: str = "intermediate") -> Dict[str, Any]:
    """
    Generates a structured explanation of the provided code snippet.
    Level: 'beginner', 'intermediate', or 'advanced'.
    """
    lang = language.lower()
    lvl = level.lower()
    if lvl not in ("beginner", "intermediate", "advanced"):
        lvl = "intermediate"

    lines = [l.strip() for l in code.splitlines() if l.strip()]
    
    # 1. Identify primary constructs
    has_loops = bool(re.search(r"\b(for|while)\b", code))
    has_recursion = False
    has_classes = bool(re.search(r"\bclass\b|\bstruct\b", code))
    has_conditionals = bool(re.search(r"\b(if|elif|else)\b", code))
    has_arrays = bool(re.search(r"\[.*?\]|std::vector|Vec<", code))

    # Look for function names
    fn_names = []
    if lang == "python":
        fn_names = re.findall(r"\bdef\s+([a-zA-Z_]\w*)", code)
    elif lang in ("cpp", "c++"):
        fn_names = re.findall(r"\b[a-zA-Z_]\w*\s+([a-zA-Z_]\w*)\s*\(", code)
        fn_names = [f for f in fn_names if f not in ("if", "while", "for", "switch", "main")]
    elif lang in ("javascript", "js"):
        fn_names = re.findall(r"\bfunction\s+([a-zA-Z_]\w*)|(?:const|let|var)\s+([a-zA-Z_]\w*)\s*=\s*\(", code)
        fn_names = [f[0] or f[1] for f in fn_names if f[0] or f[1]]
    elif lang == "rust":
        fn_names = re.findall(r"\bfn\s+([a-zA-Z_]\w*)", code)
        fn_names = [f for f in fn_names if f != "main"]

    # Check for recursion
    for fn in fn_names:
        if re.search(rf"\b{fn}\s*\(", code[code.find(fn) + len(fn):]):
            has_recursion = True
            break

    # 2. Time and Space Complexity Heuristics
    nested_loops = len(re.findall(r"(for|while).*?\n\s+(for|while)", code))
    time_complexity = "O(1)"
    space_complexity = "O(1)"

    if has_recursion:
        time_complexity = "O(2^n) or O(n) depending on recurrence"
        space_complexity = "O(n) (call stack depth)"
    elif nested_loops >= 1:
        time_complexity = "O(n²)"
        space_complexity = "O(n)" if has_arrays else "O(1)"
    elif has_loops:
        time_complexity = "O(n)"
        space_complexity = "O(n)" if has_arrays else "O(1)"

    # 3. Formulate Summary
    summary = ""
    if lvl == "beginner":
        summary = (
            f"This {lang.title()} code is a structured script that executes step by step. "
            f"It organizes tasks using {len(fn_names)} function(s) and processes data systematically."
        )
    elif lvl == "intermediate":
        summary = (
            f"A structured {lang.title()} implementation utilizing "
            f"{'iterative control flow' if has_loops else 'direct sequential evaluation'}"
            f"{' with recursive decomposition' if has_recursion else ''}. "
            f"It manages state through scoped variables and deterministic branches."
        )
    else:  # advanced
        summary = (
            f"An algorithmic routine in {lang.title()} exhibiting {time_complexity} time complexity "
            f"and {space_complexity} auxiliary space characteristics. "
            f"Employs idiomatic memory management and control-flow dispatch."
        )

    # 4. Step-by-step logic breakdown
    steps: List[Dict[str, str]] = []
    step_num = 1

    if fn_names:
        for fn in fn_names:
            steps.append({
                "step": f"Function Declaration: `{fn}`",
                "detail": f"Defines a reusable procedure named `{fn}` to isolate logic and accept input parameters."
            })
            step_num += 1

    if has_conditionals:
        steps.append({
            "step": f"Branching Logic",
            "detail": "Evaluates conditional expressions (`if`/`else`) to route execution based on dynamic runtime data."
        })
        step_num += 1

    if has_loops:
        steps.append({
            "step": f"Loop Traversal",
            "detail": "Iterates across data ranges or collections to transform, accumulate, or search elements sequentially."
        })
        step_num += 1

    if has_recursion:
        steps.append({
            "step": f"Recursive Self-Invocation",
            "detail": "Solves smaller sub-problems by having functions call themselves until reaching a designated base case."
        })
        step_num += 1

    # 5. Language-specific idioms
    idioms = []
    if lang == "python":
        idioms.append("Dynamic Duck Typing: Variables infer types automatically at runtime without explicit declarations.")
        idioms.append("Zero-indexing and first-class collection structures (`list`, `dict`).")
    elif lang in ("cpp", "c++"):
        idioms.append("Static Type Safety: Variables are bound to fixed types evaluated and checked at compile time.")
        idioms.append("RAII (Resource Acquisition Is Initialization): Resources and heap buffers are managed deterministically.")
    elif lang in ("javascript", "js"):
        idioms.append("Event-Loop Architecture & Prototype Object Model.")
        idioms.append("Flexible scoping with `const` and `let` adhering to block boundaries.")
    elif lang == "rust":
        idioms.append("Zero-Cost Abstractions: Compiles to bare-metal machine instructions without garbage collector overhead.")
        idioms.append("Affinity & Ownership: Guarantees memory safety and eliminates data races at compile time via borrow checks.")

    return {
        "level": lvl,
        "language": lang,
        "executive_summary": summary,
        "time_complexity": time_complexity,
        "space_complexity": space_complexity,
        "functions_detected": fn_names,
        "algorithmic_steps": steps,
        "language_idioms": idioms
    }

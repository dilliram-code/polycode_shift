"""
PolyShift - Static Code Analyzer
Computes metrics, cyclomatic complexity, nesting depth, and structural insights.
"""
import re
from typing import Dict, Any, List

def analyze_code_metrics(code: str, language: str) -> Dict[str, Any]:
    """
    Computes detailed code metrics for Python, C++, JavaScript, or Rust code.
    """
    lines = code.splitlines()
    total_loc = len(lines)
    blank_lines = sum(1 for line in lines if not line.strip())
    
    # Comments detection
    comment_lines = 0
    for line in lines:
        stripped = line.strip()
        if language == "python" and stripped.startswith("#"):
            comment_lines += 1
        elif language in ("cpp", "javascript", "rust") and (stripped.startswith("//") or stripped.startswith("/*")):
            comment_lines += 1

    code_lines = total_loc - blank_lines - comment_lines

    # Detect functions, classes, loops, conditionals
    function_count = 0
    class_count = 0
    loop_count = 0
    conditional_count = 0
    variable_count = 0
    return_count = len(re.findall(r"\breturn\b", code))

    if language == "python":
        function_count = len(re.findall(r"\bdef\s+[a-zA-Z_]\w*", code))
        class_count = len(re.findall(r"\bclass\s+[a-zA-Z_]\w*", code))
        loop_count = len(re.findall(r"\b(for|while)\b.*?:", code))
        conditional_count = len(re.findall(r"\b(if|elif)\b.*?:", code))
        variable_count = len(re.findall(r"^[ \t]*[a-zA-Z_]\w*\s*=", code, re.MULTILINE))
    elif language in ("cpp", "c++"):
        function_count = len(re.findall(r"\b[a-zA-Z_]\w*\s+[a-zA-Z_]\w*\s*\([^)]*\)\s*\{", code))
        class_count = len(re.findall(r"\b(class|struct)\s+[a-zA-Z_]\w*", code))
        loop_count = len(re.findall(r"\b(for|while)\s*\(", code))
        conditional_count = len(re.findall(r"\b(if|else\s+if)\s*\(", code))
        variable_count = len(re.findall(r"\b(int|double|float|bool|auto|std::string|std::vector<.*?>)\s+[a-zA-Z_]\w*", code))
    elif language in ("javascript", "js"):
        function_count = len(re.findall(r"\bfunction\s+[a-zA-Z_]\w*|=>\s*\{?", code))
        class_count = len(re.findall(r"\bclass\s+[a-zA-Z_]\w*", code))
        loop_count = len(re.findall(r"\b(for|while)\s*\(", code))
        conditional_count = len(re.findall(r"\b(if|else\s+if)\s*\(", code))
        variable_count = len(re.findall(r"\b(const|let|var)\s+[a-zA-Z_]\w*", code))
    elif language == "rust":
        function_count = len(re.findall(r"\bfn\s+[a-zA-Z_]\w*", code))
        class_count = len(re.findall(r"\bstruct\s+[a-zA-Z_]\w*", code))
        loop_count = len(re.findall(r"\b(for|while|loop)\b", code))
        conditional_count = len(re.findall(r"\bif\b", code))
        variable_count = len(re.findall(r"\blet\s+(mut\s+)?[a-zA-Z_]\w*", code))

    # Cyclomatic Complexity = Decision points + 1
    # Decision points: if, elif, while, for, &&, ||, case
    decision_points = len(re.findall(r"\b(if|elif|else\s+if|while|for|case)\b|&&|\|\|", code))
    cyclomatic_complexity = max(1, decision_points + 1)

    # Nesting depth estimation
    max_nesting = 0
    current_nesting = 0
    for line in lines:
        if language == "python":
            indent_spaces = len(line) - len(line.lstrip(" "))
            if line.strip():
                depth = indent_spaces // 4
                if depth > max_nesting:
                    max_nesting = depth
        else:
            current_nesting += line.count("{") - line.count("}")
            if current_nesting > max_nesting:
                max_nesting = current_nesting

    # Code quality / complexity rating
    complexity_rating = "Low"
    if cyclomatic_complexity > 10:
        complexity_rating = "High"
    elif cyclomatic_complexity > 5:
        complexity_rating = "Moderate"

    diagnostics = []
    if max_nesting >= 4:
        diagnostics.append(f"Deep nesting detected (level {max_nesting}). Consider refactoring or extracting helper functions.")
    if cyclomatic_complexity > 12:
        diagnostics.append(f"High cyclomatic complexity ({cyclomatic_complexity}). Recommend decomposing complex conditional branches.")
    if total_loc > 100 and function_count <= 1:
        diagnostics.append("Monolithic code detected. Recommend dividing into modular single-responsibility functions.")

    return {
        "loc": total_loc,
        "code_lines": code_lines,
        "blank_lines": blank_lines,
        "comment_lines": comment_lines,
        "function_count": function_count,
        "class_count": class_count,
        "loop_count": loop_count,
        "conditional_count": conditional_count,
        "variable_count": variable_count,
        "return_count": return_count,
        "cyclomatic_complexity": cyclomatic_complexity,
        "nesting_depth": max_nesting,
        "complexity_rating": complexity_rating,
        "diagnostics": diagnostics
    }


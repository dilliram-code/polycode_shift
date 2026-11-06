"""
PolyShift - Language Auto-Detection Engine
Analyzes syntax tokens, keywords, and structural idioms to determine the language.
"""
import re
from typing import Dict, Tuple

LANGUAGE_SIGNATURES: Dict[str, list[tuple[str, int]]] = {
    "rust": [
        (r"\bfn\s+[a-zA-Z_]\w*\s*\(", 15),
        (r"\blet\s+mut\s+", 15),
        (r"\bprintln!\s*\(", 15),
        (r"\bvec!\[", 12),
        (r"->\s*(i32|i64|u32|u64|usize|String|bool|Option|Result)\b", 12),
        (r"\bpub\s+fn\b", 12),
        (r"\bimpl\s+[A-Z]\w*", 12),
        (r"\bmatch\s+.*\s*\{", 10),
        (r"\buse\s+std::", 12),
        (r"&(mut\s+)?self\b", 10),
    ],
    "cpp": [
        (r"#include\s*<[a-zA-Z0-9_.]+>", 18),
        (r"\bstd::(cout|cin|vector|string|map|endl|make_shared)\b", 16),
        (r"\bcout\s*<<", 15),
        (r"\bcin\s*>>", 15),
        (r"\bint\s+main\s*\(\s*(int\s+argc|\))", 14),
        (r"\btemplate\s*<", 12),
        (r"\bnullptr\b", 10),
        (r"\bstd::vector<", 14),
        (r"\bpublic\s*:", 8),
        (r"\bprivate\s*:", 8),
    ],
    "javascript": [
        (r"\bconsole\.log\s*\(", 15),
        (r"\bconst\s+[a-zA-Z_]\w*\s*=", 12),
        (r"\blet\s+[a-zA-Z_]\w*\s*=", 10),
        (r"\bvar\s+[a-zA-Z_]\w*\s*=", 8),
        (r"=>\s*\{?", 10),
        (r"\bfunction\s+[a-zA-Z_]\w*\s*\(", 10),
        (r"\bdocument\.", 12),
        (r"\bwindow\.", 10),
        (r"===|!==", 10),
        (r"\bexport\s+(default|const|function)\b", 10),
        (r"\brequire\s*\(", 10),
    ],
    "python": [
        (r"\bdef\s+[a-zA-Z_]\w*\s*\(.*?\)\s*:", 16),
        (r"\belif\s+.*?:", 14),
        (r"\bclass\s+[a-zA-Z_]\w*(\(.*?\))?\s*:", 12),
        (r"\bimport\s+[a-zA-Z_]\w*", 8),
        (r"\bfrom\s+[a-zA-Z_]\w*\s+import\b", 12),
        (r"\bprint\s*\(.*?\)", 10),
        (r"\b(True|False|None)\b", 8),
        (r"\bself\.[a-zA-Z_]\w*", 10),
        (r":\s*$", 6),
        (r"\bif\s+__name__\s*==\s*['\"]__main__['\"]:", 16),
    ]
}

def detect_language(code: str) -> Tuple[str, float]:
    """
    Detects language among 'python', 'cpp', 'javascript', 'rust'.
    Returns (detected_language, confidence_score_between_0_and_1).
    """
    if not code or not code.strip():
        return "python", 0.0

    scores = {lang: 0 for lang in LANGUAGE_SIGNATURES}

    for lang, patterns in LANGUAGE_SIGNATURES.items():
        for pattern, weight in patterns:
            matches = len(re.findall(pattern, code, re.MULTILINE))
            if matches > 0:
                scores[lang] += weight * min(matches, 3)

    best_lang = max(scores, key=lambda l: scores[l])
    total_score = sum(scores.values())

    if total_score == 0:
        # Fallback heuristic
        if "{" in code and ";" in code:
            return "javascript", 0.4
        return "python", 0.4

    confidence = min(round(scores[best_lang] / max(total_score, 1), 2), 0.99)
    return best_lang, confidence


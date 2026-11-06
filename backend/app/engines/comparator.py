"""
PolyShift - Code Comparison Engine
Computes structural, semantic, and textual differences between source and translated code.
"""
import difflib
from typing import Dict, Any, List

def compare_code_snippets(
    source_code: str,
    target_code: str,
    source_language: str,
    target_language: str
) -> Dict[str, Any]:
    """
    Computes visual diff and semantic mapping between two code snippets.
    """
    src_lines = source_code.splitlines()
    tgt_lines = target_code.splitlines()

    matcher = difflib.SequenceMatcher(None, src_lines, tgt_lines)
    similarity_ratio = round(matcher.ratio(), 3)

    diff_lines = list(difflib.unified_diff(
        src_lines,
        tgt_lines,
        fromfile=f"source.{source_language}",
        tofile=f"target.{target_language}",
        lineterm=""
    ))

    added_count = 0
    removed_count = 0
    modified_count = 0

    for line in diff_lines:
        if line.startswith("+") and not line.startswith("+++"):
            added_count += 1
        elif line.startswith("-") and not line.startswith("---"):
            removed_count += 1

    # Mapping of semantic constructs across languages
    construct_mappings: List[Dict[str, str]] = []
    if source_language == "python" and target_language in ("cpp", "rust"):
        construct_mappings.append({
            "source_construct": "def func(...):",
            "target_construct": "fn func(...) -> ... / Type func(...)",
            "description": "Dynamic function signature converted to explicit type annotations."
        })
        construct_mappings.append({
            "source_construct": "print(...)",
            "target_construct": "std::cout << ... / println!(...)",
            "description": "Standard output mapped to typed stream/macro."
        })

    return {
        "source_language": source_language,
        "target_language": target_language,
        "similarity_ratio": similarity_ratio,
        "added_lines": added_count,
        "removed_lines": removed_count,
        "modified_lines": min(added_count, removed_count),
        "total_source_lines": len(src_lines),
        "total_target_lines": len(tgt_lines),
        "unified_diff": "\n".join(diff_lines),
        "construct_mappings": construct_mappings
    }


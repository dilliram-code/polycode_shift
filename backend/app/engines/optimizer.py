"""
PolyShift - Code Optimization Assistant
Identifies performance bottlenecks, redundant allocations, and language-specific optimizations.
"""
import re
from typing import Dict, Any, List

def optimize_code(code: str, language: str) -> Dict[str, Any]:
    """
    Analyzes code for performance bottlenecks and generates an optimized version with explanations.
    """
    lang = language.lower()
    optimizations: List[Dict[str, str]] = []
    optimized_code = code

    # Pattern 1: String concatenation in loops
    if re.search(r"\b(for|while)\b.*?(\+=|\+).*?['\"]", code, re.DOTALL):
        if lang == "python":
            optimizations.append({
                "type": "String Accumulation in Loop",
                "impact": "High (O(n²) to O(n))",
                "description": "Repeated string concatenation '+' creates new string allocations each cycle. Use ''.join(...) or a list buffer.",
                "tradeoff": "Requires collecting elements in a list before joining."
            })
        elif lang in ("cpp", "c++"):
            optimizations.append({
                "type": "String Reallocation",
                "impact": "Medium",
                "description": "Use reserve() on std::string or prefer std::stringstream to avoid repeated memory reallocations.",
                "tradeoff": "Slightly more verbose initialization."
            })

    # Pattern 2: Python range(len(list)) instead of enumerate or direct iteration
    if lang == "python" and re.search(r"for\s+[a-zA-Z_]\w*\s+in\s+range\(\s*len\(", code):
        optimizations.append({
            "type": "Range(len(...)) Anti-pattern",
            "impact": "Medium",
            "description": "Iterating over `range(len(arr))` incurs index lookup overhead. Use `for item in arr:` or `for i, item in enumerate(arr):`.",
            "tradeoff": "None. More idiomatic and readable."
        })
        optimized_code = re.sub(
            r"for\s+([a-zA-Z_]\w*)\s+in\s+range\(\s*len\(\s*([a-zA-Z_]\w*)\s*\)\s*\):",
            r"for \1, item in enumerate(\2):",
            optimized_code
        )

    # Pattern 3: C++ vector push_back in known sized loop without reserve
    if lang in ("cpp", "c++") and "push_back" in code and "reserve" not in code:
        optimizations.append({
            "type": "Unreserved Vector Growth",
            "impact": "High (Reduces heap reallocations)",
            "description": "std::vector repeatedly reallocates and copies elements as it grows. Preallocate capacity using `vec.reserve(N)`.",
            "tradeoff": "Requires knowing or estimating the expected size beforehand."
        })

    # Pattern 4: Rust clone inside loop
    if lang == "rust" and re.search(r"\bfor\b.*?\.clone\(\)", code, re.DOTALL):
        optimizations.append({
            "type": "Unnecessary Clone in Loop",
            "impact": "High",
            "description": "Invoking `.clone()` inside a loop performs expensive heap deep-copies. Borrow by reference `&item` instead where possible.",
            "tradeoff": "Requires lifetime and borrow compliance."
        })

    # Pattern 5: JavaScript var usage instead of const/let
    if lang in ("javascript", "js") and re.search(r"\bvar\s+", code):
        optimizations.append({
            "type": "Legacy `var` Declaration",
            "impact": "Low (Safety and Engine Optimization)",
            "description": "Replace `var` with block-scoped `const` or `let` to enable modern JavaScript engine inline caches and prevent hoisting bugs.",
            "tradeoff": "Ensures lexical block scoping."
        })
        optimized_code = re.sub(r"\bvar\s+", "let ", optimized_code)

    # Pattern 6: Linear search in list when set/hash table could be O(1)
    if re.search(r"\bin\s+[a-zA-Z_]\w*\b", code) and lang == "python":
        optimizations.append({
            "type": "Lookup Complexity",
            "impact": "High (O(n) to O(1))",
            "description": "Membership testing with `in` on a `list` runs in linear O(n) time. Convert lookup containers to `set` for O(1) average lookup.",
            "tradeoff": "Sets require hashable elements and extra initialization overhead for small collections."
        })

    # General optimization note if clean
    if not optimizations:
        optimizations.append({
            "type": "Structural Review",
            "impact": "Low",
            "description": "Code structure is concise and does not exhibit common anti-patterns or redundant allocations.",
            "tradeoff": "Standard idiomatic performance maintained."
        })

    return {
        "language": lang,
        "optimizations_count": len(optimizations),
        "optimizations": optimizations,
        "original_code": code,
        "suggested_code": optimized_code
    }

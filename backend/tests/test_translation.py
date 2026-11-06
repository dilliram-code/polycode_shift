"""
PolyShift - Universal Bidirectional Translation Engine Test Suite
Tests all 12 cross-language directions and AST mapping.
"""
import pytest
from app.engines.translators.translator import translator_engine

SAMPLE_PYTHON = """
def calculate_sum(n: int) -> int:
    total = 0
    for i in range(n):
        total += i
    return total

print(calculate_sum(10))
"""

SAMPLE_CPP = """
#include <iostream>
int calculate_sum(int n) {
    int total = 0;
    for (int i = 0; i < n; i++) {
        total += i;
    }
    return total;
}

int main() {
    std::cout << calculate_sum(10) << std::endl;
    return 0;
}
"""

SAMPLE_JS = """
function calculateSum(n) {
    let total = 0;
    for (let i = 0; i < n; i++) {
        total += i;
    }
    return total;
}

console.log(calculateSum(10));
"""

SAMPLE_RUST = """
pub fn calculate_sum(n: i32) -> i32 {
    let mut total = 0;
    for i in 0..n {
        total += i;
    }
    return total;
}

fn main() {
    println!("{}", calculate_sum(10));
}
"""

LANGUAGES = ["python", "cpp", "javascript", "rust"]

@pytest.mark.parametrize("src,tgt,sample", [
    ("python", "cpp", SAMPLE_PYTHON),
    ("python", "javascript", SAMPLE_PYTHON),
    ("python", "rust", SAMPLE_PYTHON),
    ("cpp", "python", SAMPLE_CPP),
    ("cpp", "javascript", SAMPLE_CPP),
    ("cpp", "rust", SAMPLE_CPP),
    ("javascript", "python", SAMPLE_JS),
    ("javascript", "cpp", SAMPLE_JS),
    ("javascript", "rust", SAMPLE_JS),
    ("rust", "python", SAMPLE_RUST),
    ("rust", "cpp", SAMPLE_RUST),
    ("rust", "javascript", SAMPLE_RUST),
])
def test_all_12_conversion_directions(src, tgt, sample):
    result = translator_engine.translate(sample, src, tgt)
    assert result["success"] is True
    assert result["source_language"] == src
    assert result["target_language"] == tgt
    assert len(result["translated_code"].strip()) > 0
    assert result["confidence"] > 0.0

def test_auto_detection():
    result = translator_engine.translate(SAMPLE_PYTHON, "auto", "cpp")
    assert result["success"] is True
    assert result["detected_language"] == "python"
    assert "calculate_sum" in result["translated_code"]

def test_ast_summary_statistics():
    result = translator_engine.translate(SAMPLE_PYTHON, "python", "javascript")
    assert result["ast_summary"]["functions_count"] >= 1


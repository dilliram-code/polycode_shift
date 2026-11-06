"""
PolyShift - API Integration Test Suite
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "compilers_detected" in data

def test_stats_endpoint():
    resp = client.get("/api/v1/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_translations" in data
    assert data["bidirectional_directions_count"] == 12

def test_translate_api():
    payload = {
        "source_code": "def hello():\n    print('Hello World')",
        "source_language": "python",
        "target_language": "javascript"
    }
    resp = client.post("/api/v1/translate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "console.log" in data["translated_code"]
    assert data["history_id"] is not None

def test_analyze_api():
    payload = {
        "code": "def foo(x):\n    if x > 0:\n        return x * 2\n    return 0",
        "language": "python"
    }
    resp = client.post("/api/v1/analyze", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["function_count"] >= 1
    assert data["cyclomatic_complexity"] >= 2

def test_explain_api():
    payload = {
        "code": "def fib(n):\n    if n <= 1:\n        return n\n    return fib(n-1) + fib(n-2)",
        "language": "python",
        "level": "intermediate"
    }
    resp = client.post("/api/v1/explain", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "algorithmic_steps" in data
    assert len(data["algorithmic_steps"]) > 0

def test_optimize_api():
    payload = {
        "code": "for i in range(len(arr)):\n    print(arr[i])",
        "language": "python"
    }
    resp = client.post("/api/v1/optimize", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["optimizations_count"] >= 1

def test_compare_api():
    payload = {
        "source_code": "def add(a, b):\n    return a + b",
        "target_code": "function add(a, b) {\n    return a + b;\n}",
        "source_language": "python",
        "target_language": "javascript"
    }
    resp = client.post("/api/v1/compare", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "similarity_ratio" in data
    assert "unified_diff" in data

def test_examples_api():
    resp = client.get("/api/v1/examples")
    assert resp.status_code == 200
    examples = resp.json()
    assert len(examples) >= 10
    assert examples[0]["category"] == "Hello World"

def test_validate_api():
    payload = {
        "code": "print('valid python')",
        "language": "python"
    }
    resp = client.post("/api/v1/validate", json=payload)
    assert resp.status_code == 200
    assert resp.json()["valid"] is True

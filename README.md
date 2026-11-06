# PolyShift — Universal Code Translation Engine

> **Intelligent bidirectional code translation, explanation, optimization, and validation across Python, C++, JavaScript, and Rust.**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![Tests](https://img.shields.io/badge/pytest-passing-success.svg)](https://docs.pytest.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🌟 Product Vision & Capabilities

**PolyShift** is a developer workspace that translates, compares, analyzes, optimizes, and executes code across multiple programming paradigms.

Rather than relying on brittle keyword substitution or opaque LLM black-boxes, PolyShift implements a **deterministic compiler-inspired translation engine** backed by an Intermediate Representation (IR), multi-stage syntax verification, and optional neural enhancement.

### Supported Cross-Language Matrix (All 12 Directions)

| From \ To | Python | C++ | JavaScript | Rust |
| :--- | :---: | :---: | :---: | :---: |
| **Python** | 🔄 *(Refactor)* | ✅ Direct IR | ✅ Direct IR | ✅ Direct IR |
| **C++** | ✅ Direct IR | 🔄 *(Refactor)* | ✅ Direct IR | ✅ Direct IR |
| **JavaScript** | ✅ Direct IR | ✅ Direct IR | 🔄 *(Refactor)* | ✅ Direct IR |
| **Rust** | ✅ Direct IR | ✅ Direct IR | ✅ Direct IR | 🔄 *(Refactor)* |

---

## 🚀 Key Features

### 1. Intelligent Dual-Monaco Code Workspace
- Side-by-side or stacked Monaco Editor layout with syntax highlighting, minimap, line numbers, and code folding.
- Language auto-detection and language swap with smooth 360° rotation micro-interaction.
- Live intelligence sidebar displaying cyclomatic complexity, AST construct counts, and confidence metrics.

### 2. Code Explainer Engine
- Multi-tier explanations (**Beginner**, **Intermediate**, **Advanced**).
- Algorithmic execution breakdown with parameter and variable insights.
- Heuristic Time Complexity ($O(1)$, $O(n)$, $O(n^2)$, $O(\log n)$) and Space Complexity calculations.
- Deep dive into language-specific memory models and paradigms.

### 3. Code Optimization Assistant
- Detects anti-patterns (unreserved vector allocations, redundant string concatenations in loops, unidiomatic `range(len())` scans, unnecessary clones).
- Proposes optimized target code with impact ratings and trade-off evaluations.
- 1-click **"Apply to Editor"** integration.

### 4. Visual Code Comparison & Diff View
- Side-by-side Monaco Diff Editor highlighting added, removed, and modified logic.
- Semantic construct mapping (e.g., Python `def` → Rust `fn`, `print` → `std::cout`).

### 5. Sandboxed Code Execution & Validation
- Subprocess isolation with execution timeouts (`EXECUTION_TIMEOUT_SECONDS=5`).
- Host compiler availability verification (g++, clang++, node, rustc, python3).
- Real-time terminal output (stdout, stderr, exit code, and execution time in ms).

### 6. Example Library (16 Algorithmic Categories)
- Instant access to verified implementations in all 4 languages:
  * *Hello World*, *Variables & Types*, *Conditionals*, *Loops*, *Functions*, *Recursion*, *Lists & Arrays*, *Dictionaries & Maps*, *Classes & Objects*, *Inheritance*, *Polymorphism*, *Exception Handling*, *File Operations*, *Sorting Algorithms*, *Searching Algorithms*, *Data Structures*.

### 7. Translation History & Bookmarks
- Searchable SQLite history with filters for source and target languages.
- Reopen / restore past translations directly into the editor with 1 click.
- Export history to JSON or CSV.

### 8. Premium Glassmorphic Design System
- Refined dark theme (*Midnight Navy & Electric Violet*) and light theme (*Soft Off-White & Deep Slate*).
- Persisted theme settings synchronized with Monaco Editor themes.
- Responsive across desktop, laptop, tablet, and mobile devices.

---

## 🛠️ Technology Stack

- **Frontend**: HTML5, CSS3 (Glassmorphism design tokens, CSS keyframe animations), Vanilla ES6+ JavaScript, Monaco Editor via AMD loader, SVG icons.
- **Backend**: Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy, Uvicorn.
- **Engines**: AST-based universal parser, Intermediate Representation (IR), C++ / JS / Rust generators, static code analyzer.
- **Database**: SQLite (built-in, zero external setup; fully ready for PostgreSQL).
- **Testing**: Pytest, FastAPI TestClient, HTTPX.
- **Containerization**: Docker, Docker Compose.

---

## 📦 Quickstart & Installation

### Local Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/polyshift.git
   cd polyshift
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the PolyShift server**:
   ```bash
   ./scripts/run_dev.sh
   # Or directly:
   uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
   ```

5. **Open PolyShift in your browser**:
   Navigate to [http://localhost:8000](http://localhost:8000).

---

### Running with Docker

```bash
docker-compose up --build
```
The application will be accessible at `http://localhost:8000`.

---

## 🧪 Running Tests

Execute the automated test suite covering all 12 conversion directions, AST parsing, and API endpoints:

```bash
./scripts/run_tests.sh
# Or directly:
PYTHONPATH=backend pytest backend/tests/ -v
```

All 23 unit and integration tests will execute and report passing status.

---

## 📖 API Documentation

Interactive OpenAPI / Swagger documentation is available at:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Key Endpoints:
- `POST /api/v1/translate` — Translates source code across languages.
- `POST /api/v1/analyze` — Calculates complexity metrics, LOC, and construct counts.
- `POST /api/v1/explain` — Generates algorithmic breakdown and time/space complexity.
- `POST /api/v1/optimize` — Identifies anti-patterns and performance optimizations.
- `POST /api/v1/compare` — Computes visual diff and construct mappings.
- `POST /api/v1/validate` — Validates syntax and host compiler capabilities.
- `POST /api/v1/execute` — Executes code inside an isolated subprocess sandbox.
- `GET /api/v1/history` — Retrieves past translations with search and filtering.
- `GET /api/v1/examples` — Fetches curated multi-language algorithmic examples.
- `GET /api/v1/stats` — Provides live platform translation metrics.
- `GET /api/v1/health` — System diagnostics and compiler status.

---

## 🛡️ Security Considerations

PolyShift enforces strict controls for code execution:
- User code is executed in an ephemeral, isolated subprocess folder with no shared persistence.
- Hard timeouts (`EXECUTION_TIMEOUT_SECONDS=5`) prevent infinite loops and runaway tasks.
- Static pattern inspection guards against dangerous syscalls.
- Output buffers are capped at 64 KB to mitigate buffer overflow / memory flooding attacks.
- Execution operates with unprivileged system permissions.

---

## 📄 License

This project is open-source and licensed under the [MIT License](LICENSE).

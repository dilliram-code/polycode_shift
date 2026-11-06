# Contributing to PolyShift

Thank you for contributing to PolyShift — Universal Code Translation Engine!

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/polyshift.git
   cd polyshift
   ```

2. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the local development server:
   ```bash
   ./scripts/run_dev.sh
   # Or directly:
   uvicorn app.main:app --app-dir backend --reload --port 8000
   ```

5. Open your browser at `http://localhost:8000`.

## Running Tests

PolyShift includes a comprehensive test suite for all 12 conversion directions, AST parsing, and API endpoints:

```bash
./scripts/run_tests.sh
# Or directly:
PYTHONPATH=backend pytest backend/tests/ -v
```

## Adding a New Translation Direction or Optimization Rule

1. **IR Additions**: Update `backend/app/engines/ir.py` if new universal node representations are needed.
2. **Parsers**: Extend the relevant parser in `backend/app/engines/parsers/`.
3. **Generators**: Extend the target generator in `backend/app/engines/generators/`.
4. **Semantics**: Update `PAIR_SEMANTICS` in `backend/app/engines/translators/translator.py` with appropriate warnings and approximation notices.
5. **Testing**: Add regression test cases in `backend/tests/test_translation.py`.

## Code Style

- Follow **PEP 8** for all Python code.
- Keep frontend vanilla ES6+ modular and maintain clean CSS variables for theming.


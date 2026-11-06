#!/usr/bin/env bash
# PolyShift - Test Runner Script
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." >/dev/null 2>&1 && pwd )"
cd "$DIR"

if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

export PYTHONPATH="$DIR/backend"
echo "Executing PolyShift test suite with pytest..."
pytest backend/tests/ -v --tb=short


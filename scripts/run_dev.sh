#!/usr/bin/env bash
# PolyShift - Local Development Startup Script
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." >/dev/null 2>&1 && pwd )"
cd "$DIR"

if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

export PYTHONPATH="$DIR/backend"
echo "Starting PolyShift server on http://localhost:8000 ..."
python3 -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload

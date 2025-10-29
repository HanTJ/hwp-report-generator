#!/usr/bin/env bash
set -euo pipefail

echo "== HWP Report Generator - Dev Setup (Unix) =="

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$REPO_ROOT/backend"
cd "$BACKEND_DIR"

export PATH_PROJECT_HOME="$REPO_ROOT"
echo "PATH_PROJECT_HOME=$PATH_PROJECT_HOME"

# Python
if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "Python not found. Install Python 3.12+ and retry." >&2
  exit 1
fi

# venv
if [ ! -d .venv ]; then
  echo "Creating virtual environment (.venv)..."
  "$PY" -m venv .venv
fi

source .venv/bin/activate

# pip
if ! python -m pip -V >/dev/null 2>&1; then
  echo "Bootstrapping pip via ensurepip..."
  python -m ensurepip -U
fi

echo "Installing Python dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "Initializing database..."
python init_db.py

echo "Setup complete. Start server with:"
echo "  source .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"


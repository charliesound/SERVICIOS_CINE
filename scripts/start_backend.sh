#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Load .env
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Ensure PYTHONPATH includes src/
export PYTHONPATH="$REPO_ROOT/src:${PYTHONPATH:-}"

# Kill existing backend
pkill -f "uvicorn src.app:app" 2>/dev/null || true
sleep 1

# Start backend
cd "$REPO_ROOT"
"$REPO_ROOT/.venv/bin/python" -m uvicorn src.app:app --host 127.0.0.1 --port 8010 --reload > /tmp/backend.log 2>&1 &

echo "Backend starting... log: /tmp/backend.log"

#!/usr/bin/env bash
set -euo pipefail

cd /opt/SERVICIOS_CINE

if [ ! -d ".venv" ]; then
  echo "ERROR: no existe .venv"
  exit 1
fi

source .venv/bin/activate
export PYTHONPATH="$PWD/src:${PYTHONPATH:-}"

echo "Starting AILinkCinema backend..."
echo "URL: http://127.0.0.1:8010"
echo "PYTHONPATH=$PYTHONPATH"

python -m uvicorn app:app \
  --host 0.0.0.0 \
  --port 8010 \
  --reload \
  --reload-dir src

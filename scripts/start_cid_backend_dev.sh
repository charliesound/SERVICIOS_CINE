#!/usr/bin/env bash
set -euo pipefail

cd /opt/SERVICIOS_CINE

if [ ! -d ".venv" ]; then
  echo "ERROR: no existe .venv"
  exit 1
fi

source .venv/bin/activate
export PYTHONPATH="$PWD/src"
BACKEND_HOST="${BACKEND_HOST:-127.0.0.1}"

if ss -ltnp | grep -q ':8010'; then
  echo "AILinkCinema backend ya está usando el puerto 8010."
  echo "Health:"
  curl -s http://127.0.0.1:8010/health | python -m json.tool || true
  exit 0
fi

echo "Starting AILinkCinema backend..."
echo "URL: http://127.0.0.1:8010"
echo "PYTHONPATH=$PYTHONPATH"

python -m uvicorn app:app \
  --host "$BACKEND_HOST" \
  --port 8010 \
  --reload \
  --reload-dir src

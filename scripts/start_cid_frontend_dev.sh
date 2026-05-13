#!/usr/bin/env bash
set -euo pipefail

cd /opt/SERVICIOS_CINE/src_frontend

if ss -ltnp | grep -q ':3001'; then
  echo "El puerto 3001 ya está en uso."
  echo "Abre: http://localhost:3001"
  exit 0
fi

echo "Starting AILinkCinema frontend..."
echo "URL: http://localhost:3001"

npm run dev -- --host 0.0.0.0 --port 3001 --strictPort

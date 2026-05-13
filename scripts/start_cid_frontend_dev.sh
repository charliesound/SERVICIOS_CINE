#!/usr/bin/env bash
set -euo pipefail

cd /opt/SERVICIOS_CINE/src_frontend

echo "Starting AILinkCinema frontend..."
echo "URL: http://localhost:3001"

npm run dev -- --host 0.0.0.0 --port 3001

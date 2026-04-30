#!/usr/bin/env bash
set -euo pipefail

cd /opt/SERVICIOS_CINE

echo "Starting AILinkCinema/CID home demo..."
docker compose -f compose.base.yml -f compose.home.yml --env-file .env up -d --build

docker compose -f compose.base.yml -f compose.home.yml --env-file .env ps

echo "Landing:"
echo "  http://100.121.83.126"
echo "  http://100.121.83.126:3000"
echo "API:"
echo "  http://100.121.83.126:8000"
echo "ComfyUI:"
echo "  http://100.121.83.126:8188"

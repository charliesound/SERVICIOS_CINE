#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

echo "=============================================="
echo "AILinkCinema - VPS Deployment"
echo "=============================================="
echo ""

cd "${REPO_ROOT}"

echo "[1/5] Checking environment..."
if [ ! -f .env ]; then
    echo "WARNING: .env not found. Copy from .env.vps.example first!"
    echo "cp .env.vps.example .env"
    exit 1
fi

echo "[2/5] Building images..."
docker compose -f compose.base.yml -f compose.vps.yml build

echo ""
echo "[3/5] Starting services..."
docker compose -f compose.base.yml -f compose.vps.yml up -d

echo ""
echo "[4/5] Waiting for health..."
sleep 15

echo ""
echo "[5/5] Checking services..."
docker compose -f compose.base.yml -f compose.vps.yml ps

echo ""
echo "=============================================="
echo "VPS DEPLOYMENT COMPLETE"
echo "=============================================="
echo ""
echo "Public access:"
echo "  https://${PUBLIC_HOST:-ailinkcinema.example.com}"
echo ""
echo "Check health:"
echo "  curl https://${PUBLIC_HOST:-ailinkcinema.example.com}/health"
echo ""
echo "View logs:"
echo "  docker compose -f compose.base.yml -f compose.vps.yml logs -f"
echo ""
echo "Stop:"
echo "  docker compose -f compose.base.yml -f compose.vps.yml down"
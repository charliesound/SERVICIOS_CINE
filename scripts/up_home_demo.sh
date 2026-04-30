#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

echo "=============================================="
echo "AILinkCinema - Home Demo Deployment (Host Tailscale Fallback)"
echo "=============================================="
echo ""

cd "${REPO_ROOT}"

if [ -f .env ] && ! grep -Eq '^ENABLE_DEMO_ROUTES=1' .env; then
    echo "WARNING: ENABLE_DEMO_ROUTES is not explicitly enabled in .env"
    echo "         Home demo expects ENABLE_DEMO_ROUTES=1"
fi

echo "[1/4] Building images..."
docker compose -f compose.base.yml -f compose.home.yml build

echo ""
echo "[2/4] Starting services..."
docker compose -f compose.base.yml -f compose.home.yml up -d

echo ""
echo "[3/4] Waiting for health..."
sleep 10

echo ""
echo "[4/4] Checking services..."
docker compose -f compose.base.yml -f compose.home.yml ps

echo ""
echo "=============================================="
echo "HOME DEMO DEPLOYMENT COMPLETE"
echo "=============================================="
echo ""
echo "Fallback access via host Tailscale from laptop:"
echo "  Backend API: http://<TAILSCALE_IP>:8000"
echo "  Frontend:   http://<TAILSCALE_IP>:3000"
echo ""
echo "Recommended remote access:"
echo "  bash scripts/up_home_tailscale.sh"
echo ""
echo "Check health:"
echo "  curl http://localhost:8000/health"
echo ""
echo "View logs:"
echo "  docker compose -f compose.base.yml -f compose.home.yml logs -f"
echo ""
echo "Stop:"
echo "  docker compose -f compose.base.yml -f compose.home.yml down"

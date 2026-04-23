#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

echo "=============================================="
echo "AILinkCinema - Home Demo + Tailscale"
echo "=============================================="
echo ""

cd "${REPO_ROOT}"

if [ ! -f .env ]; then
    echo "ERROR: .env not found"
    echo "Copy .env.home.example to .env first"
    exit 1
fi

if ! grep -Eq '^TS_AUTHKEY=.+' .env; then
    echo "ERROR: TS_AUTHKEY missing or empty in .env"
    echo "Set TS_AUTHKEY before starting the Tailscale sidecar"
    exit 1
fi

echo "[1/4] Building images..."
docker compose -f compose.base.yml -f compose.home.yml -f compose.home.tailscale.yml build

echo ""
echo "[2/4] Starting services..."
docker compose -f compose.base.yml -f compose.home.yml -f compose.home.tailscale.yml up -d

echo ""
echo "[3/4] Waiting for health..."
sleep 12

echo ""
echo "[4/4] Checking services..."
docker compose -f compose.base.yml -f compose.home.yml -f compose.home.tailscale.yml ps

echo ""
echo "Tailnet IP / MagicDNS:"
docker compose -f compose.base.yml -f compose.home.yml -f compose.home.tailscale.yml exec tailscale tailscale ip -4 || true

echo ""
echo "=============================================="
echo "HOME DEMO + TAILSCALE READY"
echo "=============================================="
echo ""
echo "Laptop access:"
echo "  1. http://<TAILSCALE_CONTAINER_IP>"
echo "  2. http://<TS_HOSTNAME>   (if MagicDNS is enabled)"
echo ""
echo "Logs:"
echo "  docker compose -f compose.base.yml -f compose.home.yml -f compose.home.tailscale.yml logs -f tailscale reverse-proxy-tailscale"
echo ""
echo "Stop:"
echo "  docker compose -f compose.base.yml -f compose.home.yml -f compose.home.tailscale.yml down"

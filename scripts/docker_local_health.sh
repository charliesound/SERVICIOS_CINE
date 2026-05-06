#!/bin/bash
# scripts/docker_local_health.sh - Health check local stack
set -euo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

check() {
  local url="$1" service="$2"
  if curl -sf "$url" > /dev/null; then
    echo -e "${GREEN}PASS${NC}: $service reachable at $url"
  else
    echo -e "${RED}FAIL${NC}: $service NOT reachable at $url"
    exit 1
  fi
}

echo "=== AILinkCinema Local Health Check ==="
check "http://localhost:8010/health" "Backend"
check "http://localhost:8080" "Frontend"
echo "All services healthy."

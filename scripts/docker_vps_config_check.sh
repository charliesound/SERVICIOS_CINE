#!/bin/bash
# scripts/docker_vps_config_check.sh - Validate VPS compose files
set -euo pipefail
cd "$(dirname "$0")/.."

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

check() {
  local file="$1"
  if docker compose -f "$file" config > /dev/null 2>&1; then
    echo -e "${GREEN}PASS${NC}: $file valid"
  else
    echo -e "${RED}FAIL${NC}: $file invalid"
    docker compose -f "$file" config
    exit 1
  fi
}

echo "=== Docker VPS Config Check ==="
check "deploy/docker/docker-compose.vps.yml"
echo "All configs valid."

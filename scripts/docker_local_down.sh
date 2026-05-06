#!/bin/bash
# scripts/docker_local_down.sh - Stop local Docker stack
set -euo pipefail
cd "$(dirname "$0")/.."
docker compose -f deploy/docker/docker-compose.local.yml down
echo "Stack stopped."

#!/bin/bash
# scripts/docker_local_logs.sh - View logs
set -euo pipefail
cd "$(dirname "$0")/.."
docker compose -f deploy/docker/docker-compose.local.yml logs -f "$@"

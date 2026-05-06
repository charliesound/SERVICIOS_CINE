#!/bin/bash
# scripts/docker_local_up.sh - Start local Docker stack
set -euo pipefail

GREEN='\033[0;32m'
NC='\033[0m'

echo "Starting AILinkCinema local stack..."
cd "$(dirname "$0")/.."

if [ ! -f deploy/docker/.env.local ]; then
  echo "Creating .env.local from example..."
  cp deploy/docker/.env.local.example deploy/docker/.env.local
  echo -e "${GREEN}Edit deploy/docker/.env.local with real secrets!${NC}"
  exit 1
fi

docker compose -f deploy/docker/docker-compose.local.yml up -d --build
echo -e "${GREEN}Stack started!${NC}"
echo "Backend: http://localhost:8010"
echo "Frontend: http://localhost:8080"
echo "Health: curl http://localhost:8010/health"

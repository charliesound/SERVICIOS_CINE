#!/usr/bin/env bash
set -euo pipefail

echo "=== AI Dubbing Legal Studio — Deploy ==="

ENV=${1:-production}
COMPOSE_FILE="docker-compose.prod.yml"

if [ ! -f .env ]; then
    echo "Error: .env file not found. Copy .env.production.example to .env and configure."
    exit 1
fi

echo "Pulling latest images..."
docker compose -f "$COMPOSE_FILE" pull

echo "Starting services..."
docker compose -f "$COMPOSE_FILE" up -d --remove-orphans

echo "Running health checks..."
sleep 5
curl -sf http://localhost:8000/health && echo "Backend OK" || echo "Backend FAIL"

echo "=== Deploy complete ==="
echo "Frontend: https://$(hostname)"
echo "API:      https://$(hostname)/api"
echo "MinIO:    http://localhost:9001"

#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BASE_COMPOSE_FILE="$ROOT_DIR/deploy/docker-compose.wsl.yml"
ENV_FILE="$ROOT_DIR/.env.demo"

if [[ "${1:-}" == "--env" ]]; then
  ENV_FILE="$2"
  shift 2
fi

if [[ "$ENV_FILE" != /* ]]; then
  ENV_FILE="$ROOT_DIR/$ENV_FILE"
fi

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Env file not found: $ENV_FILE"
  exit 1
fi

if [[ $# -gt 0 ]]; then
  SERVICES=()
  for service in "$@"; do
    case "$service" in
      nginx)
        SERVICES+=(web)
        ;;
      api|web)
        SERVICES+=("$service")
        ;;
      *)
        echo "Unknown service: $service"
        echo "Allowed values: api, web, nginx"
        exit 1
        ;;
    esac
  done

  docker compose --env-file "$ENV_FILE" -f "$BASE_COMPOSE_FILE" logs -f "${SERVICES[@]}"
else
  docker compose --env-file "$ENV_FILE" -f "$BASE_COMPOSE_FILE" logs -f
fi

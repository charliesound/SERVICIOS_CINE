#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BASE_COMPOSE_FILE="$ROOT_DIR/deploy/docker-compose.wsl.yml"
ENV_FILE="$ROOT_DIR/.env.demo"
LABEL=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --env)
      ENV_FILE="$2"
      shift 2
      ;;
    --label)
      LABEL="-$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1"
      echo "Usage: scripts/demo_backup.sh [--env <file>] [--label <name>]"
      exit 1
      ;;
  esac
done

if [[ "$ENV_FILE" != /* ]]; then
  ENV_FILE="$ROOT_DIR/$ENV_FILE"
fi

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Env file not found: $ENV_FILE"
  exit 1
fi

STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_DIR="$ROOT_DIR/backups"
BACKUP_FILE="$BACKUP_DIR/api-data-${STAMP}${LABEL}.tar.gz"

mkdir -p "$BACKUP_DIR"

API_STOPPED=0
cleanup() {
  if [[ "$API_STOPPED" == "1" ]]; then
    docker compose --env-file "$ENV_FILE" -f "$BASE_COMPOSE_FILE" start api >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

docker compose --env-file "$ENV_FILE" -f "$BASE_COMPOSE_FILE" stop api
API_STOPPED=1
echo "API stopped temporarily for consistent backup snapshot."

tar -czf "$BACKUP_FILE" -C "$ROOT_DIR" apps/api/data
cp "$ENV_FILE" "$BACKUP_DIR/env-${STAMP}${LABEL}.snapshot"

docker compose --env-file "$ENV_FILE" -f "$BASE_COMPOSE_FILE" start api
API_STOPPED=0
echo "API started again after backup."

echo "Backup created: $BACKUP_FILE"

#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-}"
ACTION="${2:-up}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if [[ -z "$MODE" ]]; then
  echo "Uso: ./deploy/docker/manage-docker.sh <local|vps> [up|down|logs|ps|restart]"
  exit 1
fi

if docker compose version >/dev/null 2>&1; then
  COMPOSE=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE=(docker-compose)
else
  echo "No se encontro docker compose ni docker-compose"
  exit 1
fi

case "$ACTION" in
  up) COMPOSE_ACTION=(up -d --build) ;;
  down) COMPOSE_ACTION=(down) ;;
  logs) COMPOSE_ACTION=(logs -f) ;;
  ps) COMPOSE_ACTION=(ps) ;;
  restart) COMPOSE_ACTION=(restart) ;;
  *)
    echo "Accion no soportada: $ACTION"
    exit 1
    ;;
esac

run_local() {
  cd "$ROOT_DIR"
  "${COMPOSE[@]}" -f deploy/docker/docker-compose.local.yml --env-file deploy/docker/.env.local "${COMPOSE_ACTION[@]}"
}

run_vps() {
  local vps_user="${VPS_USER:-}"
  local vps_host="${VPS_HOST:-}"
  local vps_path="${VPS_PATH:-/opt/SERVICIOS_CINE}"

  if [[ -z "$vps_user" || -z "$vps_host" ]]; then
    echo "Para modo vps necesitas VPS_USER y VPS_HOST"
    exit 1
  fi

  local remote_cmd
  remote_cmd="cd '$vps_path' && "
  if [[ "${COMPOSE[0]} ${COMPOSE[1]:-}" == "docker compose" ]]; then
    remote_cmd+="docker compose -f deploy/docker/docker-compose.vps.yml --env-file deploy/docker/.env.vps ${COMPOSE_ACTION[*]}"
  else
    remote_cmd+="docker-compose -f deploy/docker/docker-compose.vps.yml --env-file deploy/docker/.env.vps ${COMPOSE_ACTION[*]}"
  fi

  ssh "${vps_user}@${vps_host}" "$remote_cmd"
}

case "$MODE" in
  local) run_local ;;
  vps) run_vps ;;
  *)
    echo "Modo no soportado: $MODE"
    exit 1
    ;;
esac

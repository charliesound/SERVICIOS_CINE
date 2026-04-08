#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BASE_COMPOSE_FILE="$ROOT_DIR/deploy/docker-compose.wsl.yml"
AUTH_COMPOSE_FILE="$ROOT_DIR/deploy/docker-compose.wsl.demo-auth.yml"
ENV_FILE="$ROOT_DIR/.env.demo"
WITH_BASIC_AUTH="0"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --env)
      ENV_FILE="$2"
      shift 2
      ;;
    --with-basic-auth)
      WITH_BASIC_AUTH="1"
      shift
      ;;
    *)
      echo "Unknown argument: $1"
      echo "Usage: scripts/demo_start.sh [--env <file>] [--with-basic-auth]"
      exit 1
      ;;
  esac
done

if [[ "$ENV_FILE" != /* ]]; then
  ENV_FILE="$ROOT_DIR/$ENV_FILE"
fi

PREFLIGHT_ARGS=(--env "$ENV_FILE")
if [[ "$WITH_BASIC_AUTH" == "1" ]]; then
  PREFLIGHT_ARGS+=(--with-basic-auth)
fi

"$ROOT_DIR/scripts/demo_preflight.sh" "${PREFLIGHT_ARGS[@]}" --allow-stopped

read_env_value() {
  local key="$1"
  local default_value="$2"
  local raw_value
  raw_value="$(grep -E "^${key}=" "$ENV_FILE" | tail -n 1 | cut -d '=' -f2- | tr -d '\r' || true)"
  raw_value="${raw_value#${raw_value%%[![:space:]]*}}"
  raw_value="${raw_value%${raw_value##*[![:space:]]}}"
  if [[ -z "$raw_value" ]]; then
    echo "$default_value"
  else
    echo "$raw_value"
  fi
}

WEB_PORT_BIND="$(read_env_value "WEB_PORT_BIND" "8080")"
PROJECT_URL="http://127.0.0.1:${WEB_PORT_BIND}"
CORS_ORIGINS="$(read_env_value "CORS_ORIGINS" "")"
DEMO_BASIC_AUTH_USER="$(read_env_value "DEMO_BASIC_AUTH_USER" "")"
DEMO_BASIC_AUTH_PASS="$(read_env_value "DEMO_BASIC_AUTH_PASS" "")"

COMPOSE_ARGS=(--env-file "$ENV_FILE" -f "$BASE_COMPOSE_FILE")

if [[ "$WITH_BASIC_AUTH" == "1" ]]; then
  if ! command -v openssl >/dev/null 2>&1; then
    echo "openssl is required for --with-basic-auth"
    exit 1
  fi

  if [[ -z "$DEMO_BASIC_AUTH_USER" || -z "$DEMO_BASIC_AUTH_PASS" ]]; then
    echo "DEMO_BASIC_AUTH_USER and DEMO_BASIC_AUTH_PASS are required in env file for --with-basic-auth"
    exit 1
  fi

  mkdir -p "$ROOT_DIR/deploy/secrets"
  HASHED_PASS="$(openssl passwd -apr1 "$DEMO_BASIC_AUTH_PASS")"
  printf "%s:%s\n" "$DEMO_BASIC_AUTH_USER" "$HASHED_PASS" > "$ROOT_DIR/deploy/secrets/.htpasswd"
  chmod 600 "$ROOT_DIR/deploy/secrets/.htpasswd"

  COMPOSE_ARGS+=( -f "$AUTH_COMPOSE_FILE" )
  echo "Basic auth enabled for demo proxy."
fi

docker compose "${COMPOSE_ARGS[@]}" up -d --build
docker compose "${COMPOSE_ARGS[@]}" ps

"$ROOT_DIR/scripts/demo_preflight.sh" "${PREFLIGHT_ARGS[@]}"

AUTH_ARGS=()
if [[ "$WITH_BASIC_AUTH" == "1" ]]; then
  AUTH_ARGS=(-u "$DEMO_BASIC_AUTH_USER:$DEMO_BASIC_AUTH_PASS")
fi

echo "\nSmoke checks:"
curl -sS "${AUTH_ARGS[@]}" "$PROJECT_URL/api/health" || true
echo
OPS_STATUS="$(curl -sS "${AUTH_ARGS[@]}" "$PROJECT_URL/api/ops/status" || true)"
echo "$OPS_STATUS"
echo

echo "\nDemo stack started at: $PROJECT_URL"
if [[ -n "$CORS_ORIGINS" ]]; then
  echo "Expected remote origin(s): $CORS_ORIGINS"
fi
if grep -q '"reachable"[[:space:]]*:[[:space:]]*false' <<<"$OPS_STATUS"; then
  echo "Warning: ComfyUI currently unreachable. Demo can continue in storage/editor fallback mode."
fi
if [[ "$WITH_BASIC_AUTH" == "1" ]]; then
  echo "Use browser credentials user='${DEMO_BASIC_AUTH_USER}'"
fi

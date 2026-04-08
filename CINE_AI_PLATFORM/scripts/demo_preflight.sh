#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BASE_COMPOSE_FILE="$ROOT_DIR/deploy/docker-compose.wsl.yml"
AUTH_COMPOSE_FILE="$ROOT_DIR/deploy/docker-compose.wsl.demo-auth.yml"

ENV_FILE="$ROOT_DIR/.env.demo"
WITH_BASIC_AUTH="0"
ALLOW_STOPPED="0"

E_USAGE=1
E_PREREQ=2
E_CONFIG=3
E_STACK=4
E_HTTP=5

EXIT_CODE=0
FAILS=0
WARNS=0

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
    --allow-stopped)
      ALLOW_STOPPED="1"
      shift
      ;;
    *)
      echo "Unknown argument: $1"
      echo "Usage: scripts/demo_preflight.sh [--env <file>] [--with-basic-auth] [--allow-stopped]"
      exit "$E_USAGE"
      ;;
  esac
done

if [[ "$ENV_FILE" != /* ]]; then
  ENV_FILE="$ROOT_DIR/$ENV_FILE"
fi

pass() {
  echo "[PASS] $1"
}

warn() {
  echo "[WARN] $1"
  WARNS=$((WARNS + 1))
}

fail() {
  local code="$1"
  local message="$2"
  echo "[FAIL] $message"
  FAILS=$((FAILS + 1))
  if [[ "$EXIT_CODE" -eq 0 ]]; then
    EXIT_CODE="$code"
  fi
}

need_cmd() {
  local cmd="$1"
  if command -v "$cmd" >/dev/null 2>&1; then
    pass "Command available: $cmd"
  else
    fail "$E_PREREQ" "Missing command: $cmd"
  fi
}

need_cmd docker
need_cmd curl

if [[ ! -f "$BASE_COMPOSE_FILE" ]]; then
  fail "$E_CONFIG" "Compose file not found: $BASE_COMPOSE_FILE"
else
  pass "Compose file found: $BASE_COMPOSE_FILE"
fi

if [[ ! -f "$ENV_FILE" ]]; then
  fail "$E_CONFIG" "Env file not found: $ENV_FILE"
else
  pass "Env file found: $ENV_FILE"
fi

if [[ "$FAILS" -gt 0 ]]; then
  echo "Preflight failed early (${FAILS} failures)."
  exit "$EXIT_CODE"
fi

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
CORS_ORIGINS="$(read_env_value "CORS_ORIGINS" "")"
ENABLE_LEGACY_ROUTES="$(read_env_value "ENABLE_LEGACY_ROUTES" "true")"
COMFYUI_BASE_URL="$(read_env_value "COMFYUI_BASE_URL" "")"
COMFYUI_TIMEOUT_SECONDS="$(read_env_value "COMFYUI_TIMEOUT_SECONDS" "2.5")"
DEMO_BASIC_AUTH_USER="$(read_env_value "DEMO_BASIC_AUTH_USER" "")"
DEMO_BASIC_AUTH_PASS="$(read_env_value "DEMO_BASIC_AUTH_PASS" "")"
DEMO_URL="http://127.0.0.1:${WEB_PORT_BIND}"

if [[ "$WEB_PORT_BIND" =~ ^[0-9]+$ ]]; then
  pass "WEB_PORT_BIND is numeric: $WEB_PORT_BIND"
else
  fail "$E_CONFIG" "WEB_PORT_BIND must be numeric"
fi

if [[ -n "$CORS_ORIGINS" ]]; then
  pass "CORS_ORIGINS configured"
else
  fail "$E_CONFIG" "CORS_ORIGINS is empty"
fi

if [[ "$ENABLE_LEGACY_ROUTES" == "false" ]]; then
  pass "ENABLE_LEGACY_ROUTES=false (demo-hardened)"
else
  warn "ENABLE_LEGACY_ROUTES is not false"
fi

if [[ -d "$ROOT_DIR/apps/api/data" ]]; then
  pass "Persistent data directory exists: apps/api/data"
else
  fail "$E_CONFIG" "Persistent data directory missing: apps/api/data"
fi

if docker compose --env-file "$ENV_FILE" -f "$BASE_COMPOSE_FILE" config >/dev/null; then
  pass "docker compose config is valid"
else
  fail "$E_CONFIG" "docker compose config is invalid"
fi

if [[ "$WITH_BASIC_AUTH" == "1" ]]; then
  if [[ -f "$AUTH_COMPOSE_FILE" ]]; then
    pass "Auth compose override found"
  else
    fail "$E_CONFIG" "Auth compose override missing: $AUTH_COMPOSE_FILE"
  fi

  if [[ -n "$DEMO_BASIC_AUTH_USER" ]] && [[ -n "$DEMO_BASIC_AUTH_PASS" ]]; then
    pass "Demo basic auth credentials provided"
  else
    fail "$E_CONFIG" "Missing DEMO_BASIC_AUTH_USER/DEMO_BASIC_AUTH_PASS for --with-basic-auth"
  fi
fi

if [[ "$FAILS" -gt 0 ]]; then
  echo "Preflight failed before runtime checks: $FAILS failure(s), $WARNS warning(s)."
  exit "$EXIT_CODE"
fi

RUNNING_SERVICES="$(docker compose --env-file "$ENV_FILE" -f "$BASE_COMPOSE_FILE" ps --services --status running || true)"
STACK_RUNNING="0"

if grep -q '^api$' <<<"$RUNNING_SERVICES" && grep -q '^web$' <<<"$RUNNING_SERVICES"; then
  pass "Compose runtime detected (api/web running)"
  STACK_RUNNING="1"
else
  if [[ "$ALLOW_STOPPED" == "1" ]]; then
    warn "Demo stack not running (api/web). Runtime endpoint checks skipped"
  else
    fail "$E_STACK" "Demo stack is not running (api/web). Run scripts/demo_start.sh first"
  fi
fi

if [[ "$ALLOW_STOPPED" == "1" ]]; then
  if [[ "$FAILS" -gt 0 ]]; then
    echo "Preflight failed before runtime checks: $FAILS failure(s), $WARNS warning(s)."
    exit "$EXIT_CODE"
  fi

  echo "Preflight OK (config-only mode): 0 failures, $WARNS warning(s)."
  exit 0
fi

AUTH_ARGS=()
if [[ "$WITH_BASIC_AUTH" == "1" ]]; then
  AUTH_ARGS=(-u "${DEMO_BASIC_AUTH_USER}:${DEMO_BASIC_AUTH_PASS}")
fi

frontend_resp="$(curl -sS -o /dev/null -w "%{http_code}" "${AUTH_ARGS[@]}" "$DEMO_URL/" || true)"
if [[ "$frontend_resp" == "200" ]]; then
  pass "Frontend responds at $DEMO_URL (HTTP 200)"
else
  fail "$E_HTTP" "Frontend check failed at $DEMO_URL (HTTP $frontend_resp)"
fi

health_resp="$(curl -sS "${AUTH_ARGS[@]}" "$DEMO_URL/api/health" || true)"
if grep -q '"ok"[[:space:]]*:[[:space:]]*true' <<<"$health_resp"; then
  pass "API health endpoint OK"
else
  fail "$E_HTTP" "API health endpoint failed"
fi

details_resp="$(curl -sS "${AUTH_ARGS[@]}" "$DEMO_URL/api/health/details" || true)"
if grep -q '"health"' <<<"$details_resp"; then
  pass "API health/details endpoint OK"
else
  fail "$E_HTTP" "API health/details endpoint failed"
fi

ops_resp="$(curl -sS "${AUTH_ARGS[@]}" "$DEMO_URL/api/ops/status" || true)"
if grep -q '"ok"' <<<"$ops_resp"; then
  pass "Operational status endpoint OK (/api/ops/status)"
else
  warn "Operational status endpoint not reachable (/api/ops/status)"
fi

storage_resp="$(curl -sS "${AUTH_ARGS[@]}" "$DEMO_URL/api/storage/summary" || true)"
if grep -q '"ok"[[:space:]]*:[[:space:]]*true' <<<"$storage_resp"; then
  pass "Storage summary endpoint OK"
else
  fail "$E_HTTP" "Storage summary endpoint failed"
fi

if grep -q '"comfyui"' <<<"$details_resp"; then
  pass "ComfyUI integration status present in health/details"
  if grep -q '"reachable"[[:space:]]*:[[:space:]]*true' <<<"$details_resp"; then
    pass "ComfyUI reported reachable"
  else
    warn "ComfyUI reported unreachable (demo can continue in degraded mode)"
  fi
else
  fail "$E_HTTP" "ComfyUI integration status missing in health/details"
fi

if [[ -n "$COMFYUI_BASE_URL" ]]; then
  if curl -sS --max-time "$COMFYUI_TIMEOUT_SECONDS" "$COMFYUI_BASE_URL/system_stats" >/dev/null; then
    pass "Direct ComfyUI probe reachable at $COMFYUI_BASE_URL"
  else
    warn "Direct ComfyUI probe failed at $COMFYUI_BASE_URL"
  fi
else
  warn "COMFYUI_BASE_URL is empty"
fi

if [[ "$FAILS" -gt 0 ]]; then
  echo "Preflight failed: $FAILS failure(s), $WARNS warning(s). exit_code=$EXIT_CODE"
  exit "$EXIT_CODE"
fi

echo "Preflight OK: 0 failures, $WARNS warning(s)."

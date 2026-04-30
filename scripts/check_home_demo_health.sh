#!/usr/bin/env bash
set -u

cd /opt/SERVICIOS_CINE

TAILSCALE_IP="100.121.83.126"
if [ -f .env ]; then
  env_ip=$(grep -E '^TAILSCALE_IP=' .env | head -n 1 | cut -d '=' -f2- || true)
  if [ -n "${env_ip}" ]; then
    TAILSCALE_IP="${env_ip}"
  fi
fi

FAILURES=0
WARNINGS=0

pass() {
  printf 'PASS    %s\n' "$1"
}

warn() {
  WARNINGS=$((WARNINGS + 1))
  printf 'WARNING %s\n' "$1"
}

fail() {
  FAILURES=$((FAILURES + 1))
  printf 'FAIL    %s\n' "$1"
}

check_url() {
  local label="$1"
  local url="$2"
  local ok=0
  for _ in 1 2 3 4 5; do
    if curl -fsS --max-time 8 "$url" >/dev/null 2>&1; then
      ok=1
      break
    fi
    sleep 2
  done
  if [ "$ok" -eq 1 ]; then
    pass "$label -> $url"
  else
    fail "$label -> $url"
  fi
}

check_optional_url() {
  local label="$1"
  local url="$2"
  local ok=0
  for _ in 1 2 3; do
    if curl -fsS --max-time 8 "$url" >/dev/null 2>&1; then
      ok=1
      break
    fi
    sleep 1
  done
  if [ "$ok" -eq 1 ]; then
    pass "$label -> $url"
  else
    warn "$label -> $url"
  fi
}

check_api_health() {
  local label="$1"
  local base="$2"
  local ok=0
  local target="$base/health"
  for _ in 1 2 3 4 5; do
    if curl -fsS --max-time 8 "$base/health" >/dev/null 2>&1; then
      ok=1
      target="$base/health"
      break
    fi
    if curl -fsS --max-time 8 "$base/api/health" >/dev/null 2>&1; then
      ok=1
      target="$base/api/health"
      break
    fi
    sleep 2
  done
  if [ "$ok" -eq 1 ]; then
    pass "$label -> $target"
  else
    fail "$label -> $base/health or $base/api/health"
  fi
}

echo "Checking docker compose services..."
if docker compose -f compose.base.yml -f compose.home.yml --env-file .env ps; then
  pass "docker compose ps"
else
  fail "docker compose ps"
fi

echo
echo "Checking local URLs..."
check_url "Landing local" "http://127.0.0.1"
check_url "Frontend local" "http://127.0.0.1:3000"
check_api_health "API local" "http://127.0.0.1:8000"

echo
echo "Checking Tailscale URLs..."
check_url "Landing tailscale" "http://${TAILSCALE_IP}"
check_url "Frontend tailscale" "http://${TAILSCALE_IP}:3000"
check_api_health "API tailscale" "http://${TAILSCALE_IP}:8000"

echo
echo "Checking ComfyUI (optional)..."
check_optional_url "ComfyUI local" "http://127.0.0.1:8188/system_stats"
check_optional_url "ComfyUI tailscale" "http://${TAILSCALE_IP}:8188/system_stats"

echo
if [ "$FAILURES" -gt 0 ]; then
  echo "FAIL: ${FAILURES} critical checks failed, ${WARNINGS} warnings"
  exit 1
fi

if [ "$WARNINGS" -gt 0 ]; then
  echo "WARNING: no critical failures, ${WARNINGS} warnings"
  exit 0
fi

echo "PASS: all checks passed"

#!/bin/bash
# audit_docker_readiness.sh - Check Docker setup without running containers
set -euo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

failures=0
warnings=0
passes=0

pass() {
  echo -e "${GREEN}PASS${NC}: $1"
  passes=$((passes + 1))
}

fail_msg() {
  echo -e "${RED}FAIL${NC}: $1"
  failures=$((failures + 1))
}

warn_msg() {
  echo -e "${YELLOW}WARN${NC}: $1"
  warnings=$((warnings + 1))
}

echo "=== Docker Readiness Audit ==="
echo

echo "--- Dockerfiles ---"
[ -f /opt/SERVICIOS_CINE/src/Dockerfile ] && pass "Backend Dockerfile exists" || fail_msg "Backend Dockerfile missing"
[ -f /opt/SERVICIOS_CINE/src_frontend/Dockerfile ] && pass "Frontend Dockerfile exists" || fail_msg "Frontend Dockerfile missing"
[ -f /opt/SERVICIOS_CINE/.dockerignore ] && pass ".dockerignore exists" || warn_msg ".dockerignore missing"
[ -f /opt/SERVICIOS_CINE/docker-compose.yml ] && pass "docker-compose.yml exists" || warn_msg "docker-compose.yml missing"

echo

echo "--- .dockerignore Coverage ---"
for pattern in 'OLD/' '.venv/' '*.db' 'src/.venv/' 'scratch/'; do
  if grep -qF "$pattern" /opt/SERVICIOS_CINE/.dockerignore 2>/dev/null; then
    pass ".dockerignore excludes: $pattern"
  else
    warn_msg ".dockerignore missing: $pattern"
  fi
done

echo

echo "--- Config Templates ---"
[ -f /opt/SERVICIOS_CINE/.env.example ] && pass ".env.example exists" || fail_msg ".env.example missing"
find /opt/SERVICIOS_CINE/deploy -name '.env.example' 2>/dev/null | grep -q . && pass "deploy .env.example exists" || warn_msg "deploy .env.example missing"

echo

echo "--- Docker Compose Validation ---"
if command -v docker >/dev/null 2>&1; then
  local_compose="/opt/SERVICIOS_CINE/deploy/docker/docker-compose.local.yml"
  vps_compose="/opt/SERVICIOS_CINE/deploy/docker/docker-compose.vps.yml"
  [ -f "$local_compose" ] && docker compose -f "$local_compose" config >/dev/null 2>&1 && pass "docker compose config local" || warn_msg "docker compose config local unavailable"
  [ -f "$vps_compose" ] && docker compose -f "$vps_compose" config >/dev/null 2>&1 && pass "docker compose config vps" || warn_msg "docker compose config vps unavailable"
else
  warn_msg "docker not installed, skipping compose validation"
fi

echo

echo "=== Summary ==="
echo -e "${GREEN}PASS${NC}: $passes checks passed"
echo -e "${RED}FAIL${NC}: $failures checks failed"
echo -e "${YELLOW}WARN${NC}: $warnings warnings"

if [ "$failures" -gt 0 ]; then
  exit 1
fi

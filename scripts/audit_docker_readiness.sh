#!/bin/bash
# audit_docker_readiness.sh - Check Docker setup without running containers
set -euo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

failures=0
warnings=0

check() {
  local msg="$1"
  shift
  if eval "$@" >/dev/null 2>&1; then
    echo -e "${GREEN}PASS${NC}: $msg"
  else
    echo -e "${RED}FAIL${NC}: $msg"
    ((failures++))
  fi
}

warn() {
  local msg="$1"
  shift
  if eval "$@" >/dev/null 2>&1; then
    echo -e "${GREEN}PASS${NC}: $msg"
  else
    echo -e "${YELLOW}WARN${NC}: $msg"
    ((warnings++))
  fi
}

echo "=== Docker Readiness Audit ==="
echo

# 1. Dockerfiles exist
echo "--- Dockerfiles ---"
check "Backend Dockerfile exists" "ls /opt/SERVICIOS_CINE/src/Dockerfile"
check "Frontend Dockerfile exists" "ls /opt/SERVICIOS_CINE/src_frontend/Dockerfile"
warn ".dockerignore exists" "ls /opt/SERVICIOS_CINE/.dockerignore"
warn "docker-compose.yml exists" "ls /opt/SERVICIOS_CINE/docker-compose.yml"
echo

# 2. .dockerignore coverage
echo "--- .dockerignore Coverage ---"
for pattern in "OLD/" ".venv/" "*.db" "src/.venv/" "scratch/"; do
  if grep -qE "$pattern" /opt/SERVICIOS_CINE/.dockerignore 2>/dev/null; then
    echo -e "${GREEN}PASS${NC}: .dockerignore excludes: $pattern"
  else
    echo -e "${YELLOW}WARN${NC}: .dockerignore missing: $pattern"
    ((warnings++))
  fi
done
echo

# 3. Config templates
echo "--- Config Templates ---"
check ".env.example exists" "ls /opt/SERVICIOS_CINE/.env.example"
warn "docker/.env.example exists" "find /opt/SERVICIOS_CINE/deploy -name '.env.example' 2>/dev/null | grep -q ."
echo

# 4. Validate docker-compose if exists
echo "--- Docker Compose Validation ---"
if command -v docker &> /dev/null && ls /opt/SERVICIOS_CINE/docker-compose*.yml 2>/dev/null | head -1 | grep -q .; then
  for f in /opt/SERVICIOS_CINE/docker-compose*.yml; do
    warn "docker compose config $f" "docker compose -f $f config >/dev/null 2>&1"
  done
else
  echo -e "${YELLOW}WARN${NC}: docker or compose file not found, skipping"
  ((warnings++))
fi
echo

echo "=== Summary ==="
echo -e "${GREEN}PASS${NC}: $(( 10 - failures )) checks passed"
echo -e "${RED}FAIL${NC}: $failures checks failed"
echo -e "${YELLOW}WARN${NC}: $warnings warnings"
echo

if [ $failures -gt 0 ]; then
  exit 1
fi
exit 0

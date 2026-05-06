#!/bin/bash
# audit_project_integrity.sh - Non-destructive project integrity audit
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
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

echo "=== AILinkCinema Project Integrity Audit ==="
echo

# 1. Git status
echo "--- Git Status ---"
git status --short
echo

# 2. Forbidden files
echo "--- Forbidden Files Check ---"
for pattern in "\.db$" "\.db-wal$" "\.db-shm$" "\.env$" "^OLD/" "^\.venv/" "^src/\.venv/" "^scratch/"; do
  if git ls-files | grep -qE "$pattern"; then
    echo -e "${RED}FAIL${NC}: Found forbidden files matching: $pattern"
    ((failures++))
  else
    echo -e "${GREEN}PASS${NC}: No forbidden files: $pattern"
  fi
done
echo

# 3. OLD/ isolation
echo "--- OLD/ Isolation ---"
warn "OLD/ in .gitignore" "grep -q 'OLD/' /opt/SERVICIOS_CINE/.gitignore"
warn "OLD/ in .dockerignore" "grep -q 'OLD/' /opt/SERVICIOS_CINE/.dockerignore"
check "OLD/ not imported in src/" "grep -r 'OLD/' /opt/SERVICIOS_CINE/src 2>/dev/null | grep -v '.gitignore' | [ \$(wc -l) -eq 0 ]"
echo

# 4. Docker readiness
echo "--- Docker Readiness ---"
warn "Dockerfile exists" "ls /opt/SERVICIOS_CINE/src/Dockerfile"
warn "Frontend Dockerfile exists" "ls /opt/SERVICIOS_CINE/src_frontend/Dockerfile"
warn ".dockerignore exists" "ls /opt/SERVICIOS_CINE/.dockerignore"
echo

# 5. Backend health
echo "--- Backend Health ---"
check "Backend /health" "curl -s http://127.0.0.1:8010/health | grep -q 'healthy'"
echo

# 6. Frontend build
echo "--- Frontend Build ---"
check "Frontend npm run build" "cd /opt/SERVICIOS_CINE/src_frontend && npm run build 2>&1 | grep -q 'built'"

echo
echo "=== Summary ==="
echo -e "${GREEN}PASS${NC}: $(( $(git ls-files | wc -l) - failures )) checks passed"
echo -e "${RED}FAIL${NC}: $failures checks failed"
echo -e "${YELLOW}WARN${NC}: $warnings warnings"

if [ $failures -gt 0 ]; then
  exit 1
fi
exit 0

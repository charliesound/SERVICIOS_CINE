#!/bin/bash
# audit_project_integrity.sh - Non-destructive project integrity audit
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

failures=0
warnings=0
passes=0

pass() {
  echo -e "${GREEN}PASS${NC}: $1"
  ((passes++))
}

fail() {
  echo -e "${RED}FAIL${NC}: $1"
  ((failures++))
}

warn() {
  echo -e "${YELLOW}WARN${NC}: $1"
  ((warnings++))
}

echo "=== AILinkCinema Project Integrity Audit ==="
echo ""

# 1. Git status
echo "--- Git Status ---"
git status --short
echo ""

# 2. Forbidden files check (tracked files only)
echo "--- Forbidden Tracked Files Check ---"
patterns=("\.db$" "\.db-wal$" "\.db-shm$" "\.env$" "^OLD/" "^\.venv/" "^src/\.venv/" "^scratch/")
for pattern in "${patterns[@]}"; do
  if git ls-files | grep -qE "$pattern"; then
    echo -e "${RED}FAIL${NC}: Found forbidden files matching: $pattern"
    git ls-files | grep -E "$pattern" | head -20
    ((failures++))
  else
    echo -e "${GREEN}PASS${NC}: No forbidden tracked files: $pattern"
  fi
done
echo ""

# 3. Staged forbidden files check
echo "--- Staged Forbidden Files Check ---"
# Check staged area (cached) - should not have A or M for forbidden files
if git diff --cached --name-status | grep -qE '^[AM][[:space:]]+\.db$|^[AM][[:space:]]+\.db-wal$|^[AM][[:space:]]+\.db-shm$|^[AM][[:space:]]+\.env$|^[AM][[:space:]]+OLD/|^[AM][[:space:]]+\.venv/|^[AM][[:space:]]+src/\.venv/|^[AM][[:space:]]+scratch/'; then
  echo -e "${RED}FAIL${NC}: Forbidden file staged (not delete-only)"
  git diff --cached --name-status | grep -E '^[AM]' | head -20
  ((failures++))
else
  echo -e "${GREEN}PASS${NC}: No forbidden files staged (except deletes)"
fi
echo ""

# 4. OLD/ isolation
echo "--- OLD/ Isolation ---"
if grep -q '^OLD/$' .gitignore 2>/dev/null; then
  echo -e "${GREEN}PASS${NC}: OLD/ in .gitignore"
else
  echo -e "${YELLOW}WARN${NC}: OLD/ not explicitly in .gitignore"
  ((warnings++))
fi

if grep -q '^OLD/$' .dockerignore 2>/dev/null; then
  echo -e "${GREEN}PASS${NC}: OLD/ in .dockerignore"
else
  echo -e "${YELLOW}WARN${NC}: OLD/ not in .dockerignore"
  ((warnings++))
fi

# Check OLD/ not imported in src/
if grep -r 'OLD/' /opt/SERVICIOS_CINE/src 2>/dev/null | grep -v '.gitignore' | grep -q '.'; then
  echo -e "${RED}FAIL${NC}: OLD/ is referenced in src/"
  grep -r 'OLD/' /opt/SERVICIOS_CINE/src 2>/dev/null | grep -v '.gitignore' | head -10
  ((failures++))
else
  echo -e "${GREEN}PASS${NC}: OLD/ not imported in src/"
fi
echo ""

# 5. Docker readiness
echo "--- Docker Readiness ---"
if [ -f /opt/SERVICIOS_CINE/src/Dockerfile ]; then
  echo -e "${GREEN}PASS${NC}: Backend Dockerfile exists"
else
  echo -e "${YELLOW}WARN${NC}: Backend Dockerfile missing"
  ((warnings++))
fi

if [ -f /opt/SERVICIOS_CINE/src_frontend/Dockerfile ]; then
  echo -e "${GREEN}PASS${NC}: Frontend Dockerfile exists"
else
  echo -e "${YELLOW}WARN${NC}: Frontend Dockerfile missing"
  ((warnings++))
fi

if [ -f /opt/SERVICIOS_CINE/.dockerignore ]; then
  echo -e "${GREEN}PASS${NC}: .dockerignore exists"
else
  echo -e "${YELLOW}WARN${NC}: .dockerignore missing"
  ((warnings++))
fi
echo ""

# 6. Backend health
echo "--- Backend Health ---"
if curl -s http://127.0.0.1:8010/health | grep -q 'healthy'; then
  echo -e "${GREEN}PASS${NC}: Backend /health"
else
  echo -e "${YELLOW}WARN${NC}: Backend /health not reachable"
  ((warnings++))
fi
echo ""

# 7. Frontend build
echo "--- Frontend Build ---"
if cd /opt/SERVICIOS_CINE/src_frontend && npm run build 2>&1 | grep -q 'built'; then
  echo -e "${GREEN}PASS${NC}: Frontend npm run build"
else
  echo -e "${RED}FAIL${NC}: Frontend build failed"
  ((failures++))
fi
echo ""

echo "=== Summary ==="
echo -e "${GREEN}PASS${NC}: $passes checks passed"
echo -e "${RED}FAIL${NC}: $failures checks failed"
echo -e "${YELLOW}WARN${NC}: $warnings warnings"
echo ""

if [ $failures -gt 0 ]; then
  exit 1
fi
exit 0

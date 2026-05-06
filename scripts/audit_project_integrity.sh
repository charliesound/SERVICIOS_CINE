#!/bin/bash
# audit_project_integrity.sh - Non-destructive project integrity audit
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
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

echo "=== AILinkCinema Project Integrity Audit ==="
echo

echo "--- Git Status ---"
git status --short
echo

echo "--- Forbidden Tracked Files Check ---"
# OLD/ may still be in the index on branches where it is being removed.
# Track as warnings for legacy DB files already in repo, but fail on active secrets/env/venv/scratch.
for pattern in "\\.db$" "\\.db-wal$" "\\.db-shm$"; do
  matches="$(git ls-files | grep -E "$pattern" || true)"
  if [ -n "$matches" ]; then
    warn_msg "Legacy tracked files found matching: $pattern"
    echo "$matches" | head -20
  else
    pass "No tracked files: $pattern"
  fi
done

for pattern in "\\.env$" "^\\.venv/" "^src/\\.venv/" "^scratch/"; do
  matches="$(git ls-files | grep -E "$pattern" || true)"
  if [ -n "$matches" ]; then
    fail_msg "Found forbidden tracked files matching: $pattern"
    echo "$matches" | head -20
  else
    pass "No forbidden tracked files: $pattern"
  fi
done

echo

echo "--- Staged Forbidden Files Check ---"
staged_forbidden="$(git diff --cached --name-status | grep -E '^[AM][[:space:]]+.*(\.db$|\.db-wal$|\.db-shm$|\.env$)|^[AM][[:space:]]+(\.venv/|src/\.venv/|scratch/)' || true)"
if [ -n "$staged_forbidden" ]; then
  fail_msg "Forbidden .db/.env/venv/scratch files staged"
  echo "$staged_forbidden"
else
  pass "No forbidden .db/.env/venv/scratch files staged"
fi

bad_old="$(git diff --cached --name-status | awk '$2 ~ /^OLD\// && $1 != "D" {print}' || true)"
if [ -n "$bad_old" ]; then
  fail_msg "OLD/ has staged additions or modifications"
  echo "$bad_old"
else
  pass "OLD/ staged entries are deletes only or absent"
fi

echo

echo "--- OLD/ Isolation ---"
if grep -q '^OLD/' .gitignore; then
  pass "OLD/ in .gitignore"
else
  fail_msg "OLD/ missing from .gitignore"
fi

if grep -q '^OLD/' .dockerignore; then
  pass "OLD/ in .dockerignore"
else
  fail_msg "OLD/ missing from .dockerignore"
fi

old_refs="$(grep -R --exclude-dir='__pycache__' --exclude='*.pyc' -n 'OLD/' src 2>/dev/null || true)"
if [ -n "$old_refs" ]; then
  fail_msg "OLD/ referenced from src/"
  echo "$old_refs" | head -30
else
  pass "OLD/ not referenced from src/"
fi

echo

echo "--- Docker Readiness ---"
if [ -f src/Dockerfile ]; then
  pass "Backend Dockerfile exists"
else
  warn_msg "Backend Dockerfile missing"
fi

if [ -f src_frontend/Dockerfile ]; then
  pass "Frontend Dockerfile exists"
else
  warn_msg "Frontend Dockerfile missing"
fi

if [ -f .dockerignore ]; then
  pass ".dockerignore exists"
else
  fail_msg ".dockerignore missing"
fi

echo

echo "--- Backend Health ---"
if curl -s http://127.0.0.1:8010/health | grep -q 'healthy'; then
  pass "Backend /health"
else
  warn_msg "Backend /health not reachable"
fi

echo

echo "=== Summary ==="
echo -e "${GREEN}PASS${NC}: $passes checks passed"
echo -e "${RED}FAIL${NC}: $failures checks failed"
echo -e "${YELLOW}WARN${NC}: $warnings warnings"

if [ "$failures" -gt 0 ]; then
  exit 1
fi

#!/bin/bash
# audit_windows_launchers.sh - Audit .bat and .ps1 scripts for robustness
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

echo "=== Windows Launchers Audit ==="
echo

# 1. Find all .bat and .ps1
echo "--- Script Discovery ---"
shopt -s nullglob
for f in /opt/SERVICIOS_CINE/*.bat /opt/SERVICIOS_CINE/*.ps1 /opt/SERVICIOS_CINE/scripts/*.bat /opt/SERVICIOS_CINE/scripts/*.ps1; do
  echo -e "${GREEN}FOUND${NC}: $f"
done
shopt -u nullglob
echo

# 2. Check for hardcoded paths
echo "--- Hardcoded Paths Check ---"
for f in /opt/SERVICIOS_CINE/*.bat /opt/SERVICIOS_CINE/*.ps1 2>/dev/null; do
  if grep -qE "/opt/SERVICIOS_CINE|Ubuntu" "$f" 2>/dev/null; then
    echo -e "${YELLOW}WARN${NC}: $f has hardcoded WSL path (Ubuntu specific)"
    ((warnings++))
  fi
done
echo

# 3. Check for destructive commands
echo "--- Destructive Commands Check ---"
for f in /opt/SERVICIOS_CINE/*.bat /opt/SERVICIOS_CINE/*.ps1 2>/dev/null; do
  if grep -qE "git reset|rm -rf|del /|Remove-Item.*-Recurse" "$f" 2>/dev/null; then
    echo -e "${RED}FAIL${NC}: $f contains potentially destructive commands"
    ((failures++))
  else
    echo -e "${GREEN}PASS${NC}: $f no destructive commands"
  fi
done
echo

# 4. Check if scripts reference health checks
echo "--- Health Check Integration ---"
for f in /opt/SERVICIOS_CINE/*.bat /opt/SERVICIOS_CINE/*.ps1 2>/dev/null; do
  if grep -qE "health|curl|Invoke-WebRequest" "$f" 2>/dev/null; then
    echo -e "${GREEN}PASS${NC}: $f has health check"
  else
    echo -e "${YELLOW}WARN${NC}: $f missing health check"
    ((warnings++))
  fi
done
echo

echo "=== Summary ==="
echo -e "${GREEN}PASS${NC}: $(( 5 - failures )) checks passed"
echo -e "${RED}FAIL${NC}: $failures checks failed"
echo -e "${YELLOW}WARN${NC}: $warnings warnings"
echo

if [ $failures -gt 0 ]; then
  exit 1
fi
exit 0

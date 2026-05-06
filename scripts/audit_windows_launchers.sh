#!/bin/bash
# audit_windows_launchers.sh - Audit .bat and .ps1 scripts
set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

failures=0
warnings=0

echo "=== Windows Launchers Audit ==="
echo ""

# 1. Find scripts
echo "--- Script Discovery ---"
found=0
shopt -s nullglob
for f in /opt/SERVICIOS_CINE/*.bat /opt/SERVICIOS_CINE/*.ps1; do
  if [ -f "$f" ]; then
    echo -e "${GREEN}FOUND${NC}: $f"
    found=1
  fi
done
shopt -u nullglob
if [ $found -eq 0 ]; then
  echo "No .bat or .ps1 files found at root."
fi
echo ""

# 2. Check hardcoded paths
echo "--- Hardcoded Paths Check ---"
for f in /opt/SERVICIOS_CINE/*.bat /opt/SERVICIOS_CINE/*.ps1; do
  if [ -f "$f" ]; then
    if grep -qE "/opt/SERVICIOS_CINE|Ubuntu" "$f" 2>/dev/null; then
      echo -e "${YELLOW}WARN${NC}: $f has hardcoded WSL path"
      ((warnings++))
    else
      echo -e "${GREEN}PASS${NC}: $f no hardcoded paths"
    fi
  fi
done
echo ""

# 3. Check destructive commands
echo "--- Destructive Commands Check ---"
for f in /opt/SERVICIOS_CINE/*.bat /opt/SERVICIOS_CINE/*.ps1; do
  if [ -f "$f" ]; then
    if grep -qE "git reset|rm -rf|del /|Remove-Item.*-Recurse" "$f" 2>/dev/null; then
      echo -e "${RED}FAIL${NC}: $f has destructive commands"
      ((failures++))
    else
      echo -e "${GREEN}PASS${NC}: $f no destructive commands"
    fi
  fi
done
echo ""

# 4. Check health integration
echo "--- Health Check Integration ---"
for f in /opt/SERVICIOS_CINE/*.bat /opt/SERVICIOS_CINE/*.ps1; do
  if [ -f "$f" ]; then
    if grep -qE "health|curl|Invoke-WebRequest" "$f" 2>/dev/null; then
      echo -e "${GREEN}PASS${NC}: $f has health check"
    else
      echo -e "${YELLOW}WARN${NC}: $f missing health check"
      ((warnings++))
    fi
  fi
done
echo ""

echo "=== Summary ==="
echo -e "${GREEN}PASS${NC}: $(( 4 - failures )) checks passed"
echo -e "${RED}FAIL${NC}: $failures checks failed"
echo -e "${YELLOW}WARN${NC}: $warnings warnings"
echo ""

if [ $failures -gt 0 ]; then
  exit 1
fi
exit 0

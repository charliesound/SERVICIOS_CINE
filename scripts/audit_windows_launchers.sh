#!/bin/bash
# audit_windows_launchers.sh - Audit .bat and .ps1 scripts for robustness
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

echo "=== Windows Launchers Audit ==="
echo

mapfile -t launchers < <(
  find /opt/SERVICIOS_CINE \
    -path /opt/SERVICIOS_CINE/OLD -prune -o \
    \( -iname "*.bat" -o -iname "*.ps1" \) -print | sort
)

echo "--- Script Discovery ---"
if [ "${#launchers[@]}" -eq 0 ]; then
  warn_msg "No .bat/.ps1 launchers found"
else
  for f in "${launchers[@]}"; do
    echo -e "${GREEN}FOUND${NC}: $f"
  done
fi

echo

echo "--- Hardcoded Paths Check ---"
if [ "${#launchers[@]}" -eq 0 ]; then
  warn_msg "No launchers to inspect for hardcoded paths"
else
  for f in "${launchers[@]}"; do
    if grep -qE '/opt/SERVICIOS_CINE|Ubuntu' "$f" 2>/dev/null; then
      warn_msg "$f has hardcoded WSL path or distro reference"
    else
      pass "$f avoids hardcoded WSL path/distro"
    fi
  done
fi

echo

echo "--- Destructive Commands Check ---"
if [ "${#launchers[@]}" -eq 0 ]; then
  warn_msg "No launchers to inspect for destructive commands"
else
  for f in "${launchers[@]}"; do
    if grep -qE 'git reset|rm -rf|del /|Remove-Item.*-Recurse' "$f" 2>/dev/null; then
      fail_msg "$f contains potentially destructive commands"
    else
      pass "$f no destructive commands"
    fi
  done
fi

echo

echo "--- Health Check Integration ---"
if [ "${#launchers[@]}" -eq 0 ]; then
  warn_msg "No launchers to inspect for health checks"
else
  for f in "${launchers[@]}"; do
    if grep -qEi 'health|curl|Invoke-WebRequest|Invoke-RestMethod' "$f" 2>/dev/null; then
      pass "$f has health check"
    else
      warn_msg "$f missing health check"
    fi
  done
fi

echo

echo "=== Summary ==="
echo -e "${GREEN}PASS${NC}: $passes checks passed"
echo -e "${RED}FAIL${NC}: $failures checks failed"
echo -e "${YELLOW}WARN${NC}: $warnings warnings"

if [ "$failures" -gt 0 ]; then
  exit 1
fi

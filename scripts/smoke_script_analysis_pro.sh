#!/usr/bin/env bash
# Smoke: CID Script Analysis Pro
#
# Validates backend endpoints for Script Analysis Pro:
#   - Health
#   - Module catalog
#   - Analysis summary (if PROJECT_ID + TOKEN provided)
#   - Export JSON (if PROJECT_ID + TOKEN provided)
#   - Export Markdown (if PROJECT_ID + TOKEN provided)
#
# Usage:
#   ./scripts/smoke_script_analysis_pro.sh
#   BASE_URL=http://localhost:8010 TOKEN=xxx PROJECT_ID=yyy ./scripts/smoke_script_analysis_pro.sh
#
# Variables:
#   BASE_URL  - Backend URL (default: http://127.0.0.1:8010)
#   TOKEN     - JWT for authenticated endpoints (optional)
#   PROJECT_ID - Project ID for analysis/export tests (optional)

set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8010}"
TMP_DIR=".tmp/smoke_script_analysis_pro"
mkdir -p "$TMP_DIR"
FAILS=0

AUTH_ARGS=()
if [ -n "${TOKEN:-}" ]; then
  AUTH_ARGS=(-H "Authorization: Bearer $TOKEN")
fi

red() { printf "\033[31m%s\033[0m\n" "$1"; }
green() { printf "\033[32m%s\033[0m\n" "$1"; }

echo "===== SMOKE: CID Script Analysis Pro ====="
echo "BASE_URL=$BASE_URL"
echo "TOKEN=${TOKEN:+set}"
echo "PROJECT_ID=${PROJECT_ID:-}"
echo

# 1. Health
echo -n "1) Health... "
HTTP_CODE=$(curl -sS -o "$TMP_DIR/health.json" -w "%{http_code}" "$BASE_URL/health" 2>/dev/null || true)
if [ "$HTTP_CODE" = "200" ]; then
  green "OK"
else
  red "FAIL (HTTP $HTTP_CODE)"
  FAILS=$((FAILS + 1))
fi

# 2. Module catalog — script_analysis must exist
echo -n "2) Module catalog (script_analysis exists)... "
HTTP_CODE=$(curl -sS -o "$TMP_DIR/catalog.json" -w "%{http_code}" "$BASE_URL/api/modules/catalog" 2>/dev/null || true)
if [ "$HTTP_CODE" = "200" ] && jq -e '.modules[] | select(.key=="script_analysis")' "$TMP_DIR/catalog.json" > /dev/null 2>&1; then
  green "OK"
else
  red "FAIL (HTTP $HTTP_CODE or script_analysis not found)"
  FAILS=$((FAILS + 1))
fi

# 3. Module catalog — has required fields
echo -n "3) Module catalog fields... "
if [ "$HTTP_CODE" = "200" ]; then
  MODULE_NAME=$(jq -r '.modules[] | select(.key=="script_analysis") | .name' "$TMP_DIR/catalog.json" 2>/dev/null || echo "")
  FEATURE_FLAG=$(jq -r '.modules[] | select(.key=="script_analysis") | .feature_flag_key' "$TMP_DIR/catalog.json" 2>/dev/null || echo "")
  if [ "$FEATURE_FLAG" = "module_script_analysis" ]; then
    green "OK ($MODULE_NAME)"
  else
    red "FAIL (missing feature_flag_key)"
    FAILS=$((FAILS + 1))
  fi
fi

# 4. My modules — if TOKEN set
if [ -n "${TOKEN:-}" ]; then
  echo -n "4) My modules... "
  HTTP_CODE=$(curl -sS -o "$TMP_DIR/my_modules.json" -w "%{http_code}" "${AUTH_ARGS[@]}" "$BASE_URL/api/modules/me" 2>/dev/null || true)
  if [ "$HTTP_CODE" = "200" ]; then
    AVAILABLE=$(jq -r '.total_available // 0' "$TMP_DIR/my_modules.json")
    LOCKED=$(jq -r '.total_locked // 0' "$TMP_DIR/my_modules.json")
    green "OK (available=$AVAILABLE locked=$LOCKED)"
  else
    red "FAIL (HTTP $HTTP_CODE)"
    FAILS=$((FAILS + 1))
  fi
else
  echo "4) My modules — SKIP (no TOKEN)"
fi

# 5-7: Require PROJECT_ID + TOKEN
if [ -n "${PROJECT_ID:-}" ] && [ -n "${TOKEN:-}" ]; then

  echo -n "5) Analysis summary... "
  HTTP_CODE=$(curl -sS -o "$TMP_DIR/summary.json" -w "%{http_code}" "${AUTH_ARGS[@]}" "$BASE_URL/api/projects/$PROJECT_ID/analysis/summary" 2>/dev/null || true)
  if [ "$HTTP_CODE" = "200" ]; then
    green "OK"
  else
    red "FAIL (HTTP $HTTP_CODE)"
    FAILS=$((FAILS + 1))
  fi

  echo -n "6) Export JSON... "
  HTTP_CODE=$(curl -sS -o "$TMP_DIR/export.json" -w "%{http_code}" "${AUTH_ARGS[@]}" "$BASE_URL/api/projects/$PROJECT_ID/analysis/export?format=json" 2>/dev/null || true)
  if [ "$HTTP_CODE" = "200" ]; then
    # Validate it parses as JSON
    if jq . "$TMP_DIR/export.json" > /dev/null 2>&1; then
      HAS_ANALYSIS=$(jq -r '.has_analysis // false' "$TMP_DIR/export.json")
      HAS_SCRIPT=$(jq -r '.has_script // false' "$TMP_DIR/export.json")
      green "OK (has_analysis=$HAS_ANALYSIS has_script=$HAS_SCRIPT)"
    else
      red "FAIL (invalid JSON)"
      FAILS=$((FAILS + 1))
    fi
  else
    red "FAIL (HTTP $HTTP_CODE)"
    FAILS=$((FAILS + 1))
  fi

  echo -n "7) Export Markdown... "
  HTTP_CODE=$(curl -sS -o "$TMP_DIR/export.md" -w "%{http_code}" "${AUTH_ARGS[@]}" "$BASE_URL/api/projects/$PROJECT_ID/analysis/export?format=md" 2>/dev/null || true)
  if [ "$HTTP_CODE" = "200" ]; then
    if head -1 "$TMP_DIR/export.md" | grep -q "^# CID Script Analysis Pro"; then
      green "OK"
    else
      red "FAIL (missing expected header)"
      FAILS=$((FAILS + 1))
    fi
  else
    red "FAIL (HTTP $HTTP_CODE)"
    FAILS=$((FAILS + 1))
  fi

else
  echo "5) Analysis summary — SKIP (no PROJECT_ID + TOKEN)"
  echo "6) Export JSON — SKIP (no PROJECT_ID + TOKEN)"
  echo "7) Export Markdown — SKIP (no PROJECT_ID + TOKEN)"
fi

# Summary
echo
if [ "$FAILS" -eq 0 ]; then
  echo "===== RESULT: ALL PASS ====="
else
  echo "===== RESULT: $FAILS FAILURES ====="
fi
exit "$FAILS"

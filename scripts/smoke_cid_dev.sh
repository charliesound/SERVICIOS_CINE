#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${CID_BASE_URL:-http://127.0.0.1:8010}"

echo "===== CID DEV SMOKE ====="
echo "BASE_URL=$BASE_URL"

echo
echo "1) Health"
curl -fsS "$BASE_URL/health" | jq .

echo
echo "2) App Registry"
APPS_TOTAL="$(curl -fsS "$BASE_URL/api/apps" | jq -r '.total')"
echo "apps=$APPS_TOTAL"
test "$APPS_TOTAL" -ge 3

echo
echo "3) Solutions Registry"
SOLUTIONS_TOTAL="$(curl -fsS "$BASE_URL/api/solutions" | jq -r 'length')"
echo "solutions=$SOLUTIONS_TOTAL"
test "$SOLUTIONS_TOTAL" -ge 7

echo
echo "4) ComfyUI Instance Registry"
COMFY_TOTAL="$(curl -fsS "$BASE_URL/api/v1/comfyui/instances" | jq -r 'length')"
echo "comfyui_instances=$COMFY_TOTAL"
test "$COMFY_TOTAL" -eq 5

echo
echo "5) ComfySearch Scan"
WORKFLOWS_TOTAL="$(curl -fsS "$BASE_URL/api/comfysearch/scan" | jq -r '.total')"
echo "comfysearch_workflows=$WORKFLOWS_TOTAL"
test "$WORKFLOWS_TOTAL" -ge 1

echo
echo "===== RESULT ====="
echo "CID DEV SMOKE: PASS"

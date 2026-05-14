#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${CID_BASE_URL:-http://127.0.0.1:8010}"
TMP_DIR=".tmp/smoke_cid_dev"
mkdir -p "$TMP_DIR"

AUTH_HEADER=()
if [ -n "${CID_TOKEN:-}" ]; then
  AUTH_HEADER=(-H "Authorization: Bearer ${CID_TOKEN}")
fi

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
if [ -n "${CID_TOKEN:-}" ]; then
  COMFY_TOTAL="$(curl -fsS "${AUTH_HEADER[@]}" "$BASE_URL/api/v1/comfyui/instances" | jq -r 'length')"
  echo "comfyui_instances=$COMFY_TOTAL"
  test "$COMFY_TOTAL" -ge 5
else
  HTTP_CODE="$(curl -sS -o "$TMP_DIR/comfyui_instances.json" -w "%{http_code}" "$BASE_URL/api/v1/comfyui/instances")"

  if [ "$HTTP_CODE" = "401" ]; then
    echo "comfyui_instances=protected_without_token"
    echo "OK: endpoint protegido correctamente. Exporta CID_TOKEN para validar el conteo real."
  elif [ "$HTTP_CODE" = "200" ]; then
    COMFY_TOTAL="$(jq -r 'length' "$TMP_DIR/comfyui_instances.json")"
    echo "comfyui_instances=$COMFY_TOTAL"
    test "$COMFY_TOTAL" -ge 5
  else
    echo "ERROR: respuesta inesperada de /api/v1/comfyui/instances: HTTP $HTTP_CODE"
    cat "$TMP_DIR/comfyui_instances.json"
    exit 1
  fi
fi

echo
echo "5) ComfySearch Scan"
COMFYSEARCH_TOTAL="$(curl -fsS "$BASE_URL/api/comfysearch/scan" | jq -r '.total')"
echo "comfysearch_workflows=$COMFYSEARCH_TOTAL"
test "$COMFYSEARCH_TOTAL" -ge 1

echo
echo "===== RESULT ====="
echo "CID DEV SMOKE: PASS"

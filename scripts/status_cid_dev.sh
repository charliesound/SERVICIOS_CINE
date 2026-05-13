#!/usr/bin/env bash
set -euo pipefail

echo "===== AILinkCinema DEV STATUS ====="

echo
echo "Backend 8010:"
if ss -ltnp | grep -q ':8010'; then
  ss -ltnp | grep ':8010'
  echo
  curl -s http://127.0.0.1:8010/health | python -m json.tool || true
else
  echo "OFFLINE"
fi

echo
echo "Frontend 3001:"
if ss -ltnp | grep -q ':3001'; then
  ss -ltnp | grep ':3001'
  echo "URL: http://localhost:3001"
else
  echo "OFFLINE"
fi

echo
echo "Backend modules:"

if curl -fsS http://127.0.0.1:8010/api/apps >/tmp/cid_apps.json 2>/dev/null; then
  echo -n "apps: "
  jq -r '.total // "unavailable"' /tmp/cid_apps.json
else
  echo "apps: unavailable"
fi

if curl -fsS http://127.0.0.1:8010/api/solutions >/tmp/cid_solutions.json 2>/dev/null; then
  echo -n "solutions: "
  jq -r 'length' /tmp/cid_solutions.json
else
  echo "solutions: unavailable"
fi

if curl -fsS http://127.0.0.1:8010/api/v1/comfyui/instances >/tmp/cid_comfyui_instances.json 2>/dev/null; then
  echo -n "comfyui_instances: "
  jq -r 'length' /tmp/cid_comfyui_instances.json
else
  echo "comfyui_instances: unavailable"
fi

if curl -fsS http://127.0.0.1:8010/api/comfysearch/scan >/tmp/cid_comfysearch_scan.json 2>/dev/null; then
  echo -n "comfysearch_workflows: "
  jq -r '.total // "unavailable"' /tmp/cid_comfysearch_scan.json
else
  echo "comfysearch_workflows: unavailable"
fi

rm -f /tmp/cid_apps.json \
      /tmp/cid_solutions.json \
      /tmp/cid_comfyui_instances.json \
      /tmp/cid_comfysearch_scan.json

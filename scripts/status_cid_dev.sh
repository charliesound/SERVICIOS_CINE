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
curl -s http://127.0.0.1:8010/api/apps | python - <<'PY' || true
import json, sys
try:
    data = json.load(sys.stdin)
    print("apps:", data.get("total"))
except Exception:
    print("apps: unavailable")
PY

curl -s http://127.0.0.1:8010/api/solutions | python - <<'PY' || true
import json, sys
try:
    data = json.load(sys.stdin)
    print("solutions:", len(data))
except Exception:
    print("solutions: unavailable")
PY

curl -s http://127.0.0.1:8010/api/v1/comfyui/instances | python - <<'PY' || true
import json, sys
try:
    data = json.load(sys.stdin)
    print("comfyui_instances:", len(data))
except Exception:
    print("comfyui_instances: unavailable")
PY

curl -s http://127.0.0.1:8010/api/comfysearch/scan | python - <<'PY' || true
import json, sys
try:
    data = json.load(sys.stdin)
    print("comfysearch_workflows:", data.get("total"))
except Exception:
    print("comfysearch_workflows: unavailable")
PY

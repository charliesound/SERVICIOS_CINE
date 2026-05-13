#!/usr/bin/env bash
set -euo pipefail

cd /opt/SERVICIOS_CINE

if [ ! -d ".venv" ]; then
  echo "ERROR: no existe .venv"
  exit 1
fi

source .venv/bin/activate
export PYTHONPATH="$PWD/src"

echo "===== CID DEV VALIDATION ====="

echo
echo "1) Python compile"
python -m py_compile \
  src/routes/comfyui_instance_routes.py \
  src/services/comfyui_instance_registry_service.py \
  src/routes/storyboard_routes.py \
  src/schemas/storyboard_schema.py \
  src/routes/app_registry_routes.py \
  src/services/app_registry.py \
  src/routes/solutions_routes.py \
  src/services/solutions_service.py \
  src/routes/comfysearch_routes.py \
  src/services/comfy_search_service.py \
  src/routes/dubbing_bridge_routes.py

echo
echo "2) Unit tests: ComfyUI Instance Registry"
python -m pytest tests/unit/test_comfyui_instance_registry.py \
                 tests/unit/test_comfyui_instance_routes.py \
                 -q

echo
echo "3) Frontend build"
cd /opt/SERVICIOS_CINE/src_frontend
npm run build

cd /opt/SERVICIOS_CINE

echo
echo "4) Backend smoke"
./scripts/smoke_cid_dev.sh

echo
echo "===== RESULT ====="
echo "CID DEV VALIDATION: PASS"

#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="/opt/SERVICIOS_CINE"

python3 -m py_compile \
  "$ROOT_DIR/src/services/comfyui_model_inventory_service.py" \
  "$ROOT_DIR/src/services/comfyui_model_classifier_service.py" \
  "$ROOT_DIR/src/services/comfyui_workflow_catalog_service.py" \
  "$ROOT_DIR/src/services/comfyui_search_service.py" \
  "$ROOT_DIR/src/services/comfyui_pipeline_builder_service.py" \
  "$ROOT_DIR/src/services/comfyui_workflow_template_service.py" \
  "$ROOT_DIR/src/services/comfyui_storyboard_render_service.py" \
  "$ROOT_DIR"/src/routes/*.py \
  "$ROOT_DIR/src/app.py" \
  "$ROOT_DIR/scripts/smoke_comfyui_search_recommend.py" \
  "$ROOT_DIR/scripts/smoke_comfyui_pipeline_builder.py" \
  "$ROOT_DIR/scripts/smoke_comfyui_storyboard_render_contract.py" \
  "$ROOT_DIR/scripts/smoke_comfyui_workflow_template_compile.py" \
  "$ROOT_DIR/scripts/smoke_project_storyboard_render_compile_auth.py"

curl -i http://127.0.0.1:8010/health

python3 "$ROOT_DIR/scripts/smoke_comfyui_search_recommend.py"
python3 "$ROOT_DIR/scripts/smoke_comfyui_pipeline_builder.py"
python3 "$ROOT_DIR/scripts/smoke_comfyui_storyboard_render_contract.py"
python3 "$ROOT_DIR/scripts/smoke_comfyui_workflow_template_compile.py"
python3 "$ROOT_DIR/scripts/smoke_project_storyboard_render_compile_auth.py"

bash "$ROOT_DIR/scripts/guard_no_db_commit.sh"

printf '\nCOMFYUI STORYBOARD CONTRACT VALIDATION PASS\n'

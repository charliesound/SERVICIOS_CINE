#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

COMFYUI_IMAGE="${COMFYUI_IMAGE:-local/comfyui-placeholder:latest}"
COMFYUI_CONTAINER_ROOT="${COMFYUI_CONTAINER_ROOT:-/root/ComfyUI}"
COMFYUI_MODELS_BASE_DIR="${COMFYUI_MODELS_BASE_DIR:-/mnt/i/COMFYUI_OK/models}"
COMFYUI_HUB_DIR="${COMFYUI_HUB_DIR:-/mnt/g/COMFYUI_HUB}"
export COMFYUI_IMAGE
export COMFYUI_CONTAINER_ROOT
export COMFYUI_MODELS_BASE_DIR
export COMFYUI_HUB_DIR

docker compose -f compose.base.yml -f compose.comfyui.yml --profile with-comfyui config >/dev/null
docker compose -f compose.base.yml -f compose.comfyui.yml -f compose.comfyui.gpu.yml --profile with-comfyui config >/dev/null

COMFYUI_STILL_HOST_PORT=8288 docker compose -f compose.base.yml -f compose.comfyui.yml --profile with-comfyui config >/dev/null
COMFYUI_STILL_HOST_PORT=8288 docker compose -f compose.base.yml -f compose.comfyui.yml -f compose.comfyui.gpu.yml --profile with-comfyui config >/dev/null

echo "PASS: ComfyUI compose skeleton config is valid (CPU/GPU overrides)."

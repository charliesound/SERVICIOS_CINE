#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

COMFYUI_IMAGE="${COMFYUI_IMAGE:-local/comfyui-placeholder:latest}"
export COMFYUI_IMAGE

docker compose -f compose.base.yml -f compose.comfyui.yml --profile with-comfyui config >/dev/null
docker compose -f compose.base.yml -f compose.comfyui.yml -f compose.comfyui.gpu.yml --profile with-comfyui config >/dev/null

echo "PASS: ComfyUI compose skeleton config is valid (CPU/GPU overrides)."

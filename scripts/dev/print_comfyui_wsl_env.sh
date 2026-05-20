#!/usr/bin/env bash
set -euo pipefail

# Print ComfyUI WSL environment variables for .env
# Usage: scripts/dev/print_comfyui_wsl_env.sh

WSL_IP="$(hostname -I | awk '{print $1}')"

if [ -z "$WSL_IP" ]; then
    echo "ERROR: could not detect WSL IP" >&2
    exit 1
fi

cat <<EOF
# ComfyUI WSL endpoints (detected IP: ${WSL_IP})
# Copy these lines into .env if IP changed after WSL/Windows restart.

COMFYUI_BASE_URL=http://${WSL_IP}:8188
COMFYUI_STILL=http://${WSL_IP}:8188
COMFYUI_STILL_BASE_URL=http://${WSL_IP}:8188
COMFYUI_STILL_URL=http://${WSL_IP}:8188
COMFYUI_STORYBOARD_BASE_URL=http://${WSL_IP}:8188
COMFYUI_VIDEO=http://${WSL_IP}:8189
COMFYUI_VIDEO_BASE_URL=http://${WSL_IP}:8189
COMFYUI_VIDEO_URL=http://${WSL_IP}:8189
COMFYUI_DUBBING=http://${WSL_IP}:8190
COMFYUI_DUBBING_BASE_URL=http://${WSL_IP}:8190
COMFYUI_DUBBING_URL=http://${WSL_IP}:8190
COMFYUI_LAB=http://${WSL_IP}:8191
COMFYUI_LAB_BASE_URL=http://${WSL_IP}:8191
COMFYUI_LAB_URL=http://${WSL_IP}:8191
COMFYUI_RESTORATION_BASE_URL=http://${WSL_IP}:8191
COMFYUI_3D_BASE_URL=http://${WSL_IP}:8192
COMFYUI_HTTP_TIMEOUT=300
COMFYUI_TIMEOUT_SECONDS=300
EOF

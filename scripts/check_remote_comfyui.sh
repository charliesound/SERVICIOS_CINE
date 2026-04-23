#!/usr/bin/env bash
# Check ComfyUI Connection (Local/Host/WSL)
# Validates ComfyUI endpoints from host or WSL for Home Demo

set -euo pipefail

# Default ports on localhost for Home Demo (ComfyUI running outside Docker)
COMFYUI_BASE_URL=${CHECK_COMFYUI_BASE_URL:-${COMFYUI_BASE_URL:-http://localhost:8188}}
COMFYUI_VIDEO_URL=${CHECK_COMFYUI_VIDEO_URL:-${COMFYUI_VIDEO_URL:-http://localhost:8189}}
COMFYUI_DUBBING_URL=${CHECK_COMFYUI_DUBBING_URL:-${COMFYUI_DUBBING_URL:-http://localhost:8190}}
COMFYUI_LAB_URL=${CHECK_COMFYUI_LAB_URL:-${COMFYUI_LAB_URL:-http://localhost:8191}}

# Requirements (can be overridden with env vars)
REQUIRE_STILL=${REQUIRE_STILL:-1}
REQUIRE_VIDEO=${REQUIRE_VIDEO:-1}
REQUIRE_DUBBING=${REQUIRE_DUBBING:-0}
REQUIRE_LAB=${REQUIRE_LAB:-0}

echo "=============================================="
echo "AILinkCinema - ComfyUI Connectivity Check"
echo "=============================================="
echo ""

check_endpoint() {
    local name="$1"
    local url="$2"
    local required="$3"
    local timeout=5
    
    local short_name="${name##COMFYUI_}"
    echo -n "[${short_name}] Checking ${url}... "
    if curl -sf --max-time ${timeout} "${url}/system_stats" >/dev/null 2>&1 || \
       curl -sf --max-time ${timeout} "${url}/history" >/dev/null 2>&1; then
        echo "OK"
        return 0
    else
        if [ "${required}" = "1" ]; then
            echo "FAILED (required)"
            return 1
        else
            echo "MISSING (optional)"
            return 2
        fi
    fi
}

ERRORS=0
WARNINGS=0

check_endpoint "COMFYUI_STILL" "${COMFYUI_BASE_URL}" "${REQUIRE_STILL}" || status=$?
if [ ${status:-0} -eq 1 ]; then ((ERRORS++)); fi
if [ ${status:-0} -eq 2 ]; then ((WARNINGS++)); fi
unset status

check_endpoint "COMFYUI_VIDEO" "${COMFYUI_VIDEO_URL}" "${REQUIRE_VIDEO}" || status=$?
if [ ${status:-0} -eq 1 ]; then ((ERRORS++)); fi
if [ ${status:-0} -eq 2 ]; then ((WARNINGS++)); fi
unset status

check_endpoint "COMFYUI_DUBBING" "${COMFYUI_DUBBING_URL}" "${REQUIRE_DUBBING}" || status=$?
if [ ${status:-0} -eq 1 ]; then ((ERRORS++)); fi
if [ ${status:-0} -eq 2 ]; then ((WARNINGS++)); fi
unset status

check_endpoint "COMFYUI_LAB" "${COMFYUI_LAB_URL}" "${REQUIRE_LAB}" || status=$?
if [ ${status:-0} -eq 1 ]; then ((ERRORS++)); fi
if [ ${status:-0} -eq 2 ]; then ((WARNINGS++)); fi
unset status

echo ""
echo "=============================================="
if [ ${ERRORS} -eq 0 ]; then
    echo "READY FOR HOME DEMO"
else
    echo "BLOCKING: ${ERRORS} required endpoint(s) unreachable"
fi
echo "=============================================="
echo ""

if [ ${WARNINGS} -gt 0 ]; then
    echo "Note: ${WARNINGS} optional endpoint(s) not running."
    echo "      Demo core features (Still + Video) are available."
fi

if [ ${ERRORS} -gt 0 ]; then
    echo ""
    echo "Troubleshooting:"
    echo "1. Start required ComfyUI instances:"
    echo "   - 8188 (Still): Required for image generation"
    echo "   - 8189 (Video): Required for video generation"
    echo "2. Check if ComfyUI is running: curl localhost:8188/history"
    echo "3. See docs/DEPLOY_HOME.md for details"
    exit 1
fi

exit 0
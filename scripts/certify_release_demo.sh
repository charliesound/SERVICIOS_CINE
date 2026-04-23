#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

for venv_path in "${REPO_ROOT}/src/.venv/bin/python" "${REPO_ROOT}/venv/bin/python" "${REPO_ROOT}/.venv/bin/python"; do
    if [ -f "${venv_path}" ]; then
        VENV_PYTHON="${venv_path}"
        break
    fi
done

if [ -z "${VENV_PYTHON:-}" ]; then
    if command -v python3 &>/dev/null; then
        VENV_PYTHON="python3"
    elif command -v python &>/dev/null; then
        VENV_PYTHON="python"
    else
        echo "ERROR: No Python found. Please install Python or create venv."
        exit 1
    fi
fi

echo "=============================================="
echo "AILinkCinema - Release Demo Certification"
echo "=============================================="
echo ""

echo "[1/4] Checking Python environment..."
if [ ! -f "${VENV_PYTHON}" ]; then
    echo "ERROR: Virtual environment not found at ${REPO_ROOT}/src/.venv"
    exit 1
fi
echo "OK: Python venv found"

echo ""
echo "[2/4] Running Sprint 13 Smoke Test (isolated SQLite in /tmp)..."
cd "${REPO_ROOT}"
APP_ENV=demo ENABLE_DEMO_ROUTES=1 ENABLE_EXPERIMENTAL_ROUTES=0 ENABLE_POSTPRODUCTION_ROUTES=0 "${VENV_PYTHON}" scripts/smoke_sprint13_rc.py
echo "OK: Smoke test passed"

echo ""
echo "[3/4] Validating frontend build..."
bash "${REPO_ROOT}/scripts/build_frontend_wsl.sh"
echo "OK: Frontend build passed"

echo ""
echo "[4/4] Validating documentation..."
if [ ! -f "${REPO_ROOT}/docs/SPRINT13_RUNBOOK.md" ]; then
    echo "ERROR: SPRINT13_RUNBOOK.md not found"
    exit 1
fi
echo "OK: Runbook exists"

echo ""
echo "=============================================="
echo "CERTIFICATION PASSED"
echo "=============================================="
echo ""
echo "Release is ready for commercial demos."
echo ""
echo "Demo credentials:"
echo "  demo_free@servicios-cine.com / demo123"
echo "  demo_studio@servicios-cine.com / demo123"
echo "  demo_creator@servicios-cine.com / demo123"
echo "  demo_enterprise@servicios-cine.com / demo123"
echo "  admin@servicios-cine.com / admin123"
echo ""

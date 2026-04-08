@echo off
REM Smoke tests for backend capability detection
REM Run from project root: python tests/smoke_ops.py

curl -X GET "http://localhost:8000/api/ops/instances"
echo.
echo ========================================
curl -X GET "http://localhost:8000/api/ops/capabilities"
echo.
echo ========================================
curl -X GET "http://localhost:8000/api/ops/capabilities/still"
echo.
echo ========================================
curl -X GET "http://localhost:8000/api/ops/capabilities?force_refresh=true"
echo.
echo ========================================
curl -X POST "http://localhost:8000/api/ops/instances/still/health-check"
echo.
echo ========================================
curl -X GET "http://localhost:8000/api/ops/can-run?backend=still&capabilities=image_generation,sampling"
echo.

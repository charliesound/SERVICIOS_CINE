@echo off
REM =============================================
REM SERVICIOS_CINE Smoke Tests
REM Run from project root: python tests/smoke_tests.py
REM =============================================
setlocal

echo.
echo ================================================
echo SERVICIOS_CINE Backend Smoke Tests
echo ================================================
echo.

set BASE=http://localhost:8000

echo [1/8] Testing Health...
curl -s "%BASE%/health" | findstr /C:"healthy"
echo.

echo [2/8] Testing Backend Instances...
curl -s "%BASE%/api/ops/instances"
echo.
echo.

echo [3/8] Testing Backend Capabilities...
curl -s "%BASE%/api/ops/capabilities"
echo.
echo.

echo [4/8] Testing Plan Catalog...
curl -s "%BASE%/api/plans/catalog"
echo.
echo.

echo [5/8] Testing Workflow Catalog...
curl -s "%BASE%/api/workflows/catalog"
echo.
echo.

echo [6/8] Testing User Registration...
curl -s -X POST "%BASE%/api/auth/register" ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"testuser\",\"email\":\"test@example.com\",\"password\":\"test123\"}"
echo.
echo.

echo [7/8] Testing Plan Limits Check...
curl -s "%BASE%/api/plans/me?user_id=test123&plan_name=free"
echo.
echo.

echo [8/8] Testing Queue Status...
curl -s "%BASE%/api/queue/status"
echo.
echo.

echo ================================================
echo Smoke Tests Complete
echo ================================================
endlocal

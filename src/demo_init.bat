@echo off
REM =============================================
REM SERVICIOS_CINE Demo Initialization Script
REM Run from project root
REM =============================================

echo.
echo ================================================
echo SERVICIOS_CINE Demo Setup
echo ================================================
echo.

set BASE=http://localhost:8000

echo [1/5] Checking backend health...
curl -s "%BASE%/health"
echo.
echo.

echo [2/5] Initializing demo data...
curl -s -X POST "%BASE%/api/demo/quick-start"
echo.
echo.

echo [3/5] Getting demo users...
curl -s "%BASE%/api/demo/users"
echo.
echo.

echo [4/5] Getting demo projects...
curl -s "%BASE%/api/demo/projects"
echo.
echo.

echo [5/5] Getting demo presets...
curl -s "%BASE%/api/demo/presets"
echo.
echo.

echo ================================================
echo Demo Credentials:
echo ================================================
echo.
echo FREE:     demo_free@servicios-cine.com / demo123
echo CREATOR:  demo_creator@servicios-cine.com / demo123
echo STUDIO:   demo_studio@servicios-cine.com / demo123
echo ENTERPRISE: demo_enterprise@servicios-cine.com / demo123
echo ADMIN:    admin@servicios-cine.com / admin123
echo.
echo ================================================
echo Quick Start URL:
echo ================================================
curl -s -X POST "%BASE%/api/demo/quick-start" | findstr /C:"frontend"
echo.

echo ================================================
echo Demo Setup Complete!
echo ================================================

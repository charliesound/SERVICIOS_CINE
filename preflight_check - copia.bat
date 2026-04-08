@echo off
REM SERVICIOS_CINE - Preflight Check (Batch version)
REM Ejecuta la version PowerShell

echo.
echo ========================================
echo SERVICIOS_CINE - Preflight Check
echo ========================================
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0preflight_check.ps1"

pause

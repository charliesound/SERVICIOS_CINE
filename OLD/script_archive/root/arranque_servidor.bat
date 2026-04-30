@echo off
REM SERVICIOS_CINE - Arranque Servidor (Batch version)

echo.
echo ========================================
echo SERVICIOS_CINE - Arranque Servidor
echo ========================================
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0arranque_servidor.ps1" %*

pause

@echo off
REM SERVICIOS_CINE - Copiar al Servidor (Batch version)

echo.
echo ========================================
echo SERVICIOS_CINE - Copiar al Servidor
echo ========================================
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0copiar_al_servidor.ps1" %*

pause

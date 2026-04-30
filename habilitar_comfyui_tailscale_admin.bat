@echo off
echo.
echo ========================================
echo Habilitar ComfyUI por Tailscale
echo ========================================
echo.
echo Esto abrira PowerShell como administrador para crear:
echo   - portproxy 100.121.83.126:8188 ^> 172.24.174.31:8188
echo   - firewall rule solo para Tailscale
echo.
powershell.exe -NoProfile -Command "Start-Process PowerShell -Verb RunAs -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File ""\\wsl.localhost\Ubuntu\opt\SERVICIOS_CINE\scripts\windows_enable_comfyui_tailscale.ps1""'"
echo.
echo Si aceptas el UAC, al terminar prueba:
echo   wsl.exe -d Ubuntu -- bash -lc "cd /opt/SERVICIOS_CINE && ./scripts/check_home_demo_health.sh"
echo.
pause

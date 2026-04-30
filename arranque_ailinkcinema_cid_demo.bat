@echo off
echo.
echo ========================================
echo AILinkCinema / CID - Home Demo
echo ========================================
echo.
echo Starting with compose.base.yml + compose.home.yml + .env
echo.
wsl.exe -d Ubuntu -- bash -lc "cd /opt/SERVICIOS_CINE && ./scripts/start_home_demo.sh"
echo.
echo URLs:
echo   PC local:    http://127.0.0.1
echo   Tailscale:   http://100.121.83.126
echo   Frontend:    http://100.121.83.126:3000
echo   API:         http://100.121.83.126:8000
echo.
echo Health check:
echo   wsl.exe -d Ubuntu -- bash -lc "cd /opt/SERVICIOS_CINE && ./scripts/check_home_demo_health.sh"
echo.
echo Stop command:
echo   wsl.exe -d Ubuntu -- bash -lc "cd /opt/SERVICIOS_CINE && ./scripts/stop_home_demo.sh"
echo.
pause

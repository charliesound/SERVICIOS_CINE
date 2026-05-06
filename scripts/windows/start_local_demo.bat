@echo off
setlocal EnableDelayedExpansion

REM --- Config (override as needed)
if "%WSL_DISTRO%"=="" set WSL_DISTRO=Ubuntu
if "%PROJECT_DIR%"=="" set PROJECT_DIR=/opt/SERVICIOS_CINE

echo =======================================
echo AILinkCinema / CID - Local Demo (Windows)
echo =======================================
echo.
echo Using WSL Distro: %WSL_DISTRO%
echo Project Dir: %PROJECT_DIR%
echo.

echo [1/4] Starting Docker stack...
wsl.exe -d %WSL_DISTRO% -- bash -lc "cd %PROJECT_DIR% && docker compose -f deploy/docker/docker-compose.local.yml up -d --build"
if errorlevel 1 (
  echo FAIL: Docker stack failed to start
  pause
  exit /b 1
)

echo [2/4] Waiting for backend to be ready...
:waitloop
wsl.exe -d %WSL_DISTRO% -- bash -lc "cd %PROJECT_DIR% && ./scripts/docker_local_health.sh" >nul 2>&1
if errorlevel 1 (
  timeout /t 3 >nul
  goto waitloop
)

echo [3/4] Health check...
wsl.exe -d %WSL_DISTRO% -- bash -lc "cd %PROJECT_DIR% && ./scripts/docker_local_health.sh"

echo [4/4] URLs:
echo   Frontend:  http://localhost:8080
echo   Backend:   http://localhost:8010
echo   Health:    http://localhost:8010/health
echo.
echo Opening frontend in browser...
start http://localhost:8080

pause

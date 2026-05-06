@echo off
setlocal EnableDelayedExpansion

if "%WSL_DISTRO%"=="" set WSL_DISTRO=Ubuntu
if "%PROJECT_DIR%"=="" set PROJECT_DIR=/opt/SERVICIOS_CINE

echo Checking AILinkCinema local health...
wsl.exe -d %WSL_DISTRO% -- bash -lc "cd %PROJECT_DIR% && ./scripts/docker_local_health.sh"
if errorlevel 1 (
  echo FAIL: Services not healthy
  pause
  exit /b 1
)
echo PASS: All services healthy
pause

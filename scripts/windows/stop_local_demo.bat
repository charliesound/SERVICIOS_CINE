@echo off
setlocal EnableDelayedExpansion

if "%WSL_DISTRO%"=="" set WSL_DISTRO=Ubuntu
if "%PROJECT_DIR%"=="" set PROJECT_DIR=/opt/SERVICIOS_CINE

echo Stopping AILinkCinema local stack...
wsl.exe -d %WSL_DISTRO% -- bash -lc "cd %PROJECT_DIR% && docker compose -f deploy/docker/docker-compose.local.yml down"
echo Done.
pause

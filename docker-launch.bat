@echo off
setlocal

set MODE=%~1
set ACTION=%~2

if "%MODE%"=="" set /p MODE=Modo (local/vps): 
if "%ACTION%"=="" set /p ACTION=Accion (up/down/logs/ps/restart) [up]: 
if "%ACTION%"=="" set ACTION=up

if /I "%MODE%"=="local" goto run_local
if /I "%MODE%"=="vps" goto prepare_vps

echo Modo invalido. Usa local o vps.
exit /b 1

:run_local
wsl bash -lc "cd /opt/SERVICIOS_CINE && chmod +x deploy/docker/manage-docker.sh && ./deploy/docker/manage-docker.sh local %ACTION%"
exit /b %ERRORLEVEL%

:prepare_vps
if "%VPS_USER%"=="" set /p VPS_USER=VPS user: 
if "%VPS_HOST%"=="" set /p VPS_HOST=VPS host o IP: 
if "%VPS_PATH%"=="" set /p VPS_PATH=Ruta del repo en VPS [/opt/SERVICIOS_CINE]: 
if "%VPS_PATH%"=="" set VPS_PATH=/opt/SERVICIOS_CINE

wsl bash -lc "cd /opt/SERVICIOS_CINE && chmod +x deploy/docker/manage-docker.sh && VPS_USER='%VPS_USER%' VPS_HOST='%VPS_HOST%' VPS_PATH='%VPS_PATH%' ./deploy/docker/manage-docker.sh vps %ACTION%"
exit /b %ERRORLEVEL%

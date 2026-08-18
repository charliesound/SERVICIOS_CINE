@echo off
title CID Local Media Agent V0.1
cls

echo.
echo  ======================================================
echo   CID  Local Media Agent  V0.1
echo  ======================================================
echo.
echo  Starting...
echo.

cd /d C:\Users\Carlos\AppData\Local\Temp

set WINPY=C:\Users\Carlos\AppData\Local\Programs\Python\Python312\python.exe

pushd "\\wsl.localhost\Ubuntu-24.04-CID\opt\SERVICIOS_CINE"

"%WINPY%" -m scripts.local_media_agent.cid_local_media_agent_operator %*

popd

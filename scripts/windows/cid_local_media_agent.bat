@echo off
title CID Local Media Agent V0.2
cls

echo.
echo  ======================================================
echo   CID  Local Media Agent  V0.2
echo   Scan + Metadata + Local Transcription
echo  ======================================================
echo.
echo  Starting...
echo.
echo  Usage:
echo    Double-click: Scan + Metadata only
echo    CLI: python cid_local_media_agent_operator.py --transcribe MODEL_DIR FOLDER
echo.

cd /d C:\Users\Carlos\AppData\Local\Temp

set WINPY=C:\Users\Carlos\AppData\Local\Programs\Python\Python312\python.exe

pushd "\\wsl.localhost\Ubuntu-24.04-CID\opt\SERVICIOS_CINE"

"%WINPY%" -m scripts.local_media_agent.cid_local_media_agent_operator %*

popd

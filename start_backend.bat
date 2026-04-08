@echo off
setlocal

echo ==========================================
echo   SERVICIOS_CINE - ARRANQUE BACKEND
echo ==========================================

set PROJECT_ROOT=%~dp0
set SRC_DIR=%PROJECT_ROOT%src

if not exist "%SRC_DIR%" (
    echo [ERROR] No se encuentra la carpeta src en:
    echo %SRC_DIR%
    pause
    exit /b 1
)

cd /d "%SRC_DIR%"

echo [INFO] Ruta actual:
echo %CD%

echo [INFO] Comprobando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no está disponible en PATH.
    pause
    exit /b 1
)

echo [INFO] Comprobando dependencias basicas...
python -c "import fastapi, yaml, uvicorn" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Faltan dependencias. Ejecuta antes:
    echo pip install -r requirements.txt
    pause
    exit /b 1
)

echo [INFO] Arrancando backend en 0.0.0.0:8000 ...
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload

if errorlevel 1 (
    echo [ERROR] El backend se cerró con error.
    pause
    exit /b 1
)

endlocal
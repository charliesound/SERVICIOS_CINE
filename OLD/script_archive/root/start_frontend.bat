@echo off
setlocal

echo ==========================================
echo   SERVICIOS_CINE - ARRANQUE FRONTEND
echo ==========================================

set PROJECT_ROOT=%~dp0
set FRONT_DIR=%PROJECT_ROOT%src_frontend

if not exist "%FRONT_DIR%" (
    echo [ERROR] No se encuentra la carpeta src_frontend en:
    echo %FRONT_DIR%
    pause
    exit /b 1
)

cd /d "%FRONT_DIR%"

echo [INFO] Ruta actual:
echo %CD%

echo [INFO] Comprobando Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js no está disponible en PATH.
    pause
    exit /b 1
)

echo [INFO] Comprobando npm...
npm --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] npm no está disponible en PATH.
    pause
    exit /b 1
)

if not exist "node_modules" (
    echo [INFO] No existe node_modules. Instalando dependencias...
    npm install
    if errorlevel 1 (
        echo [ERROR] Falló npm install.
        pause
        exit /b 1
    )
)

echo [INFO] Arrancando frontend...
npm run dev -- --host 0.0.0.0 --port 3000

if errorlevel 1 (
    echo [ERROR] El frontend se cerró con error.
    pause
    exit /b 1
)

endlocal
@echo off
REM AILinkCinema - Inicio Rapido
REM Inicia todos los servicios necesarios

echo.
echo ═══════════════════════════════════════════════════════
echo   AILinkCinema - Inicio Rapido
echo ═══════════════════════════════════════════════════════
echo.

set PROJECT_ROOT=%~dp0

REM Verificar si el backend ya esta corriendo
curl -s http://localhost:8000/health >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [INFO] Backend ya esta corriendo
) else (
    echo [INFO] Iniciando Backend...
    start "AILinkCinema Backend" cmd /k "cd /d "%PROJECT_ROOT%src" && python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload"
)

REM Verificar si el frontend ya esta corriendo
curl -s http://localhost:3000 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [INFO] Frontend ya esta corriendo
) else (
    echo [INFO] Iniciando Frontend...
    start "AILinkCinema Frontend" cmd /k "cd /d "%PROJECT_ROOT%src_frontend" && npm run dev -- --host 0.0.0.0 --port 3000"
)

echo.
echo ═══════════════════════════════════════════════════════
echo   Servicios iniciados
echo ═══════════════════════════════════════════════════════
echo.
echo Esperando 5 segundos para verificacion...
timeout /t 5 /nobreak >nul

curl -s http://localhost:8000/health >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Backend respondiendo en http://localhost:8000
    echo [OK] API Docs en http://localhost:8000/docs
) else (
    echo [WARN] Backend no responde aun
)

echo.
echo Accesos:
echo   Frontend: http://localhost:3000
echo   Backend:  http://localhost:8000
echo.
echo Tailscale (si configurado):
echo   http://100.121.83.126 (oailinkcinema)
echo.
echo Presiona cualquier tecla para abrir en navegador...
pause >nul

start http://localhost:3000
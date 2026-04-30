@echo off
setlocal

echo ==========================================
echo  SERVICIOS_CINE - PREFLIGHT DEL SERVIDOR
echo ==========================================

set PROJECT_ROOT=%~dp0
set SRC_DIR=%PROJECT_ROOT%src
set FRONT_DIR=%PROJECT_ROOT%src_frontend

echo.
echo [1] Verificando estructura del proyecto...

if exist "%SRC_DIR%" (
  echo   [OK] %SRC_DIR%
) else (
  echo   [FALTA] %SRC_DIR%
)

if exist "%FRONT_DIR%" (
  echo   [OK] %FRONT_DIR%
) else (
  echo   [FALTA] %FRONT_DIR%
)

if exist "%SRC_DIR%\app.py" (
  echo   [OK] %SRC_DIR%\app.py
) else (
  echo   [FALTA] %SRC_DIR%\app.py
)

if exist "%SRC_DIR%\requirements.txt" (
  echo   [OK] %SRC_DIR%\requirements.txt
) else (
  echo   [FALTA] %SRC_DIR%\requirements.txt
)

if exist "%SRC_DIR%\config\config.yaml" (
  echo   [OK] %SRC_DIR%\config\config.yaml
) else (
  echo   [FALTA] %SRC_DIR%\config\config.yaml
)

if exist "%SRC_DIR%\config\instances.yml" (
  echo   [OK] %SRC_DIR%\config\instances.yml
) else (
  echo   [FALTA] %SRC_DIR%\config\instances.yml
)

if exist "%SRC_DIR%\config\plans.yml" (
  echo   [OK] %SRC_DIR%\config\plans.yml
) else (
  echo   [FALTA] %SRC_DIR%\config\plans.yml
)

if exist "%FRONT_DIR%\package.json" (
  echo   [OK] %FRONT_DIR%\package.json
) else (
  echo   [FALTA] %FRONT_DIR%\package.json
)

echo.
echo [2] Verificando herramientas...

python --version >nul 2>&1
if errorlevel 1 (
  echo   [ERROR] Python no esta en PATH
) else (
  echo   [OK] Python disponible
)

pip --version >nul 2>&1
if errorlevel 1 (
  echo   [ERROR] pip no esta en PATH
) else (
  echo   [OK] pip disponible
)

node --version >nul 2>&1
if errorlevel 1 (
  echo   [ERROR] Node.js no esta en PATH
) else (
  echo   [OK] Node.js disponible
)

npm --version >nul 2>&1
if errorlevel 1 (
  echo   [ERROR] npm no esta en PATH
) else (
  echo   [OK] npm disponible
)

echo.
echo [3] Verificando dependencias Python minimas...

python -c "import fastapi, yaml, uvicorn, aiohttp, httpx; print('deps OK')" >nul 2>&1
if errorlevel 1 (
  echo   [ERROR] Faltan dependencias Python. Ejecuta:
  echo   pip install -r "%SRC_DIR%\requirements.txt"
) else (
  echo   [OK] Dependencias Python minimas disponibles
)

echo.
echo [4] Verificando puertos locales...
for %%P in (8000 3000 8188 8189 8190 8191) do (
  powershell -Command "if (Get-NetTCPConnection -LocalPort %%P -ErrorAction SilentlyContinue) { exit 1 } else { exit 0 }" >nul 2>&1
  if errorlevel 1 (
    echo   [OCUPADO] Puerto %%P
  ) else (
    echo   [LIBRE] Puerto %%P
  )
)

echo.
echo [5] Verificando conectividad local a backends IA...
for %%U in (
  "http://127.0.0.1:8188"
  "http://127.0.0.1:8189"
  "http://127.0.0.1:8190"
  "http://127.0.0.1:8191"
) do (
  powershell -Command "try { Invoke-WebRequest -Uri %%~U -UseBasicParsing -TimeoutSec 3 ^| Out-Null; exit 0 } catch { exit 1 }" >nul 2>&1
  if errorlevel 1 (
    echo   [WARN] No responde ahora: %%~U
  ) else (
    echo   [OK] Responde: %%~U
  )
)

echo.
echo [6] Resumen final
echo   - Proyecto raiz: %PROJECT_ROOT%
echo   - Backend: %SRC_DIR%
echo   - Frontend: %FRONT_DIR%

echo.
echo Siguiente orden recomendado:
echo   1. Arrancar backends IA ^(8188-8191^) si no estan activos
echo   2. Ejecutar start_backend.bat
echo   3. Ejecutar start_frontend.bat
echo   4. Probar desde el servidor: http://127.0.0.1:8000/health
echo   5. Probar desde el laptop: http://IP_DEL_SERVIDOR:3000

echo.
echo Preflight completado.
pause
endlocal
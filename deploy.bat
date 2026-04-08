@echo off
REM AILinkCinema - Deploy Completo con un Solo Comando
REM Ejecutar como Administrador en el servidor

echo.
echo ═══════════════════════════════════════════════════════
echo   AILinkCinema - Despliegue Automatico
echo ═══════════════════════════════════════════════════════
echo.

set PROJECT_ROOT=%~dp0
cd /d "%PROJECT_ROOT%"

REM Verificar Python
echo [1/6] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no encontrado
    echo Instalar desde: https://python.org
    pause
    exit /b 1
)
echo [OK] Python encontrado

REM Verificar Node.js
echo.
echo [2/6] Verificando Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js no encontrado
    echo Instalar desde: https://nodejs.org
    pause
    exit /b 1
)
echo [OK] Node.js encontrado

REM Instalar dependencias Python
echo.
echo [3/6] Instalando dependencias Python...
cd src
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Error instalando dependencias Python
    pause
    exit /b 1
)
echo [OK] Dependencias Python instaladas
cd ..

REM Instalar dependencias Frontend
echo.
echo [4/6] Instalando dependencias Frontend...
cd src_frontend
npm install >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Error instalando dependencias Frontend
    pause
    exit /b 1
)
echo [OK] Dependencias Frontend instaladas
cd ..

REM Verificar estructura
echo.
echo [5/6] Verificando estructura del proyecto...
if not exist "src\app.py" (
    echo [ERROR] No se encuentra src\app.py
    pause
    exit /b 1
)
if not exist "src_frontend\package.json" (
    echo [ERROR] No se encuentra src_frontend\package.json
    pause
    exit /b 1
)
if not exist "src\config\config.yaml" (
    echo [ERROR] No se encuentra src\config\config.yaml
    pause
    exit /b 1
)
echo [OK] Estructura verificada

REM Crear logs directorio
echo.
echo [6/6] Creando directorios necesarios...
if not exist "logs" mkdir logs
if not exist "data" mkdir data
if not exist "data\temp" mkdir data\temp
if not exist "data\output" mkdir data\output
echo [OK] Directorios creados

echo.
echo ═══════════════════════════════════════════════════════
echo   Despliegue completado!
echo ═══════════════════════════════════════════════════════
echo.
echo Para iniciar los servicios:
echo.
echo   Opcion 1 - Manual:
echo     start_backend.bat
echo     start_frontend.bat
echo.
echo   Opcion 2 - Consola dupla:
echo     cmd /k "python -m uvicorn app:app --port 8000"
echo     npm run dev
echo.
echo   Opcion 3 - Docker:
echo     docker-compose up -d
echo.
echo Accesos:
echo   Local:     http://localhost:3000
echo   Tailscale: http://100.121.83.126 (o ailinkcinema)
echo.
echo Credenciales demo:
echo   admin@servicios-cine.com / admin123
echo   demo_free@servicios-cine.com / demo123
echo.
pause
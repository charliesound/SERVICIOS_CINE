@echo off
REM SERVICIOS_CINE - Setup Script para primer arranque

echo.
echo ========================================
echo SERVICIOS_CINE - Setup
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Install Python 3.10+ from https://python.org
    echo.
    pause
    exit /b 1
)
echo OK

echo.
echo [2/3] Installing Python dependencies...
cd src
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: pip install failed
    pause
    exit /b 1
)
cd ..

echo.
echo [3/3] Installing Node dependencies...
cd src_frontend
if not exist package.json (
    echo ERROR: package.json not found
    cd ..
    pause
    exit /b 1
)
npm install
if errorlevel 1 (
    echo ERROR: npm install failed
    cd ..
    pause
    exit /b 1
)
cd ..

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Start ComfyUI backends (8188-8191)
echo   2. Run preflight_check.bat to verify
echo   3. Run start_backend.bat
echo   4. Run start_frontend.bat
echo.
pause

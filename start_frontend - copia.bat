@echo off
REM SERVICIOS_CINE - Start Frontend

echo.
echo ========================================
echo Starting Frontend...
echo ========================================
echo.

cd /d "%~dp0src_frontend"

REM Check node
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found
    echo Install Node.js 18+ from nodejs.org
    pause
    exit /b 1
)

REM Install dependencies
if not exist node_modules (
    echo Installing dependencies...
    npm install
    echo.
)

echo Starting Vite dev server on 0.0.0.0:3000
echo Frontend will be accessible from:
echo   - Local: http://localhost:3000
echo   - Network: http://YOUR_IP:3000
echo.
echo Note: Vite proxy will forward /api/* to backend at :8000
echo.

npm run dev -- --host 0.0.0.0

pause

@echo off
REM SERVICIOS_CINE - Start Backend

echo.
echo ========================================
echo Starting Backend...
echo ========================================
echo.

cd /d "%~dp0src"

REM Check dependencies
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found
    echo Install Python 3.10+ from python.org
    pause
    exit /b 1
)

REM Install dependencies if needed
pip install -r requirements.txt --quiet >nul 2>&1

echo Starting FastAPI backend on 0.0.0.0:8000
echo Backend will be accessible from:
echo   - Local: http://localhost:8000
echo   - Network: http://YOUR_IP:8000
echo.
echo API Docs: http://localhost:8000/docs
echo.

REM Start with uvicorn, bind to all interfaces
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload

pause

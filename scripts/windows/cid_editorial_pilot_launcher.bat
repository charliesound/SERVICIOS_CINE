@echo off
rem ===========================================================================
rem  CID Editorial Pilot Launcher - one-click local board launch
rem  Double-click to start the local editorial operator board and auto-open the
rem  default browser. Portable and relocatable: no hard-coded user / WSL / /mnt
rem  / repo-absolute paths are assumed.
rem
rem  Packaged Python resolution order:
rem    1. CID_PYTHONW environment variable (if set and the file exists)
rem    2. runtime\python\pythonw.exe relative to this launcher / package root
rem    3. runtime\python\python.exe relative to this launcher / package root
rem  No system / where / py.exe lookup. Missing packaged runtime is a concise
rem  controlled refusal with a nonzero exit.
rem ===========================================================================
setlocal

set "BASE=%~dp0"
if not "%BASE%"=="" set "BASE=%BASE:~0,-1%"

set "PYTHON_EXE="

if defined CID_PYTHONW (
    if exist "%CID_PYTHONW%" set "PYTHON_EXE=%CID_PYTHONW%"
)

if not defined PYTHON_EXE (
    if exist "%BASE%\runtime\python\pythonw.exe" (
        set "PYTHON_EXE=%BASE%\runtime\python\pythonw.exe"
    )
)

if not defined PYTHON_EXE (
    if exist "%BASE%\runtime\python\python.exe" (
        set "PYTHON_EXE=%BASE%\runtime\python\python.exe"
    )
)

if not defined PYTHON_EXE (
    echo.
    echo   CID Editorial Pilot: packaged Python runtime not found.
    echo   Expected one of:
    echo     CID_PYTHONW environment variable ^(if set^)
    echo     %BASE%\runtime\python\pythonw.exe
    echo     %BASE%\runtime\python\python.exe
    echo.
    exit /b 1
)

if exist "%BASE%\app" set "PYTHONPATH=%BASE%\app"
if not defined PYTHONPATH set "PYTHONPATH=%BASE%\app"

set "PYTHONNOUSERSITE=1"

rem Launch the pilot experience. Role defaults to PRODUCER; the browser opens
rem on the local loopback URL automatically.
"%PYTHON_EXE%" -m scripts.local_media_agent.editorial_selection_cli launch
set "EXIT_CODE=%ERRORLEVEL%"

endlocal & exit /b %EXIT_CODE%

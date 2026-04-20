@echo off
REM Backend startup script
REM This script sets up and starts the FastAPI backend

setlocal enabledelayedexpansion
set "SCRIPT_DIR=%~dp0"
set "BACKEND_DIR=!SCRIPT_DIR!..\backend"

echo.
echo ==================== ET V2 BACKEND STARTUP ====================
echo.
echo Step 1: Navigating to backend directory...
echo Path: !BACKEND_DIR!
cd /d "!BACKEND_DIR!"

if errorlevel 1 (
    echo ERROR: Failed to navigate to backend directory
    pause
    exit /b 1
)

echo [OK] Backend directory ready
echo.
echo Step 2: Installing dependencies...
echo (Note: Warning about email_validator.exe PATH is safe to ignore)
pip install -r requirements.txt --quiet --disable-pip-version-check --no-warn-script-location

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [OK] Dependencies installed
echo.
echo Step 3: Verifying uvicorn installation...
python -c "import uvicorn; print('✅ Uvicorn version:', uvicorn.__version__)" >nul 2>&1
if errorlevel 1 (
    echo WARNING: Uvicorn not found in installed packages
    echo Attempting to install or reinstall...
    pip install uvicorn --quiet --disable-pip-version-check
)

echo.
echo Step 4: Starting Uvicorn server...
echo.
echo ================================================================
echo Backend Server Starting...
echo API Docs: http://localhost:8000/docs
echo Health Check: http://localhost:8000/
echo ================================================================
echo.

REM Start the server using python -m (more reliable than direct uvicorn command)
python -m uvicorn app:app --reload --port 8000 --host 127.0.0.1

if errorlevel 1 (
    echo.
    echo ERROR: Uvicorn failed to start
    echo Possible causes:
    echo   - Port 8000 is already in use
    echo   - Missing Python dependencies
    echo   - Python import errors in app
    pause
    exit /b 1
)

pause

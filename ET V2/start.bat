@echo off
REM Main startup script for ET V2
REM This script launches backend and frontend in separate terminal windows

setlocal enabledelayedexpansion
set "ET_V2_DIR=%~dp0"
set "SCRIPTS_DIR=!ET_V2_DIR!scripts"

echo.
echo =====================================================================
echo                    🚀 ET V2 - SMART SPEND AI
echo =====================================================================
echo.
echo Loading project from: !ET_V2_DIR!
echo.

REM Check if scripts directory exists
if not exist "!SCRIPTS_DIR!" (
    echo ERROR: scripts directory not found
    echo Expected: !SCRIPTS_DIR!
    pause
    exit /b 1
)

echo Starting services...
echo.

REM Start Backend in new terminal window
echo [1/2] Launching Backend Server (port 8000)...
start "ET V2 Backend" cmd /k "call "!SCRIPTS_DIR!\start-backend.bat""

REM Wait for backend to initialize
timeout /t 3 /nobreak >nul

REM Start Frontend in new terminal window
echo [2/2] Launching Frontend Server (port 3001)...
start "ET V2 Frontend" cmd /k "call "!SCRIPTS_DIR!\start-frontend.bat""

echo.
echo =====================================================================
echo                      ✅ SERVICES LAUNCHED
echo =====================================================================
echo.
echo 📱 Frontend UI:     http://localhost:3001
echo 📚 Backend API:     http://localhost:8000/docs
echo 🏥 Health Check:    http://localhost:8000/
echo.
echo Two terminal windows should open shortly. Use Ctrl+C to stop each
echo service individually, or close both terminal windows to stop all.
echo.
echo =====================================================================
echo.
pause


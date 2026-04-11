@echo off
REM Frontend startup script
REM This script sets up and starts the React Vite development server

setlocal enabledelayedexpansion
set "SCRIPT_DIR=%~dp0"
set "FRONTEND_DIR=!SCRIPT_DIR!..\frontend"

echo.
echo ==================== ET V2 FRONTEND STARTUP ====================
echo.
echo Step 1: Navigating to frontend directory...
echo Path: !FRONTEND_DIR!
cd /d "!FRONTEND_DIR!"

if errorlevel 1 (
    echo ERROR: Failed to navigate to frontend directory
    pause
    exit /b 1
)

echo [OK] Frontend directory ready
echo.
echo Step 2: Installing dependencies...
call npm install --silent

if errorlevel 1 (
    echo ERROR: Failed to install npm dependencies
    echo Possible causes:
    echo   - Node.js not installed or not on PATH
    echo   - npm cache issues
    echo Solution: Run 'npm cache clean --force' and try again
    pause
    exit /b 1
)

echo [OK] Dependencies installed
echo.
echo Step 3: Starting Vite dev server...
echo.
echo ================================================================
echo Frontend Server Starting...
echo UI: http://localhost:3001
echo ================================================================
echo.

REM Start the dev server
call npm run dev

if errorlevel 1 (
    echo.
    echo ERROR: Vite dev server failed to start
    echo Possible causes:
    echo   - Port 3001 is already in use
    echo   - Missing npm dependencies
    pause
    exit /b 1
)

pause

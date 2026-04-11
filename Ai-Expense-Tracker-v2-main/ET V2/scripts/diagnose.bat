@echo off
REM ET V2 Diagnostic Script
REM Checks if all prerequisites are installed and accessible

setlocal enabledelayedexpansion
set "SCRIPT_DIR=%~dp0"

echo.
echo =====================================================================
echo              ET V2 SYSTEM DIAGNOSTIC TOOL
echo =====================================================================
echo.
echo Checking prerequisites for ET V2 project...
echo.

REM Check Python
echo [CHECK 1] Python Installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ FAILED: Python not found or not on PATH
    echo Solution: Install Python from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
) else (
    for /f "tokens=*" %%i in ('python --version') do set "PY_VERSION=%%i"
    echo ✅ Found: !PY_VERSION!
)
echo.

REM Check pip
echo [CHECK 2] Pip (Python Package Manager)...
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ FAILED: pip not found
    echo Solution: Reinstall Python or run: python -m ensurepip
) else (
    for /f "tokens=*" %%i in ('pip --version') do set "PIP_VERSION=%%i"
    echo ✅ Found: !PIP_VERSION!
)
echo.

REM Check Node.js
echo [CHECK 3] Node.js Installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ FAILED: Node.js not found or not on PATH
    echo Solution: Install Node.js from https://nodejs.org/
    echo Download the LTS version and check "Add to PATH" during installation
) else (
    for /f "tokens=*" %%i in ('node --version') do set "NODE_VERSION=%%i"
    echo ✅ Found: Node.js !NODE_VERSION!
)
echo.

REM Check npm
echo [CHECK 4] npm (Node Package Manager)...
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ FAILED: npm not found
    echo Solution: Reinstall Node.js (npm comes with it)
) else (
    for /f "tokens=*" %%i in ('npm --version') do set "NPM_VERSION=%%i"
    echo ✅ Found: npm !NPM_VERSION!
)
echo.

REM Check if backend directory exists
echo [CHECK 5] Backend Directory...
if exist "!SCRIPT_DIR!\..\backend" (
    echo ✅ Backend directory found
) else (
    echo ❌ FAILED: Backend directory not found
    echo Expected: !SCRIPT_DIR!\..\backend
)
echo.

REM Check if frontend directory exists
echo [CHECK 6] Frontend Directory...
if exist "!SCRIPT_DIR!\..\frontend" (
    echo ✅ Frontend directory found
) else (
    echo ❌ FAILED: Frontend directory not found
    echo Expected: !SCRIPT_DIR!\..\frontend
)
echo.

REM Check if requirements.txt exists
echo [CHECK 7] Backend Requirements File...
if exist "!SCRIPT_DIR!\..\backend\requirements.txt" (
    echo ✅ requirements.txt found
) else (
    echo ❌ FAILED: requirements.txt not found
    echo Expected: !SCRIPT_DIR!\..\backend\requirements.txt
)
echo.

REM Check if package.json exists
echo [CHECK 8] Frontend Package File...
if exist "!SCRIPT_DIR!\..\frontend\package.json" (
    echo ✅ package.json found
) else (
    echo ❌ FAILED: package.json not found
    echo Expected: !SCRIPT_DIR!\..\frontend\package.json
)
echo.

REM Check available ports
echo [CHECK 9] Port Availability...
echo Checking if port 8000 (Backend) is listening...
netstat -ano | findstr ":8000" >nul 2>&1
if errorlevel 1 (
    echo ✅ Port 8000 is available
) else (
    echo ⚠️  WARNING: Port 8000 is already in use (might cause Backend to fail)
)
echo.

echo Checking if port 3001 (Frontend) is listening...
netstat -ano | findstr ":3001" >nul 2>&1
if errorlevel 1 (
    echo ✅ Port 3001 is available
) else (
    echo ⚠️  WARNING: Port 3001 is already in use (might cause Frontend to fail)
)
echo.

echo =====================================================================
echo              END OF DIAGNOSTIC REPORT
echo =====================================================================
echo.
echo If all checks passed (all ✅), then run: start.bat
echo.
echo If you see ❌ failures:
echo   1. Install the missing software
echo   2. Add it to your PATH environment variable
echo   3. Close and reopen this terminal
echo   4. Run this diagnostic again
echo.
pause

@echo off
REM Get the directory where this batch file is located (ET V2 folder)
setlocal enabledelayedexpansion
set "ET_V2_DIR=%~dp0"

echo Installing Backend...
cd /d "!ET_V2_DIR!backend"
call pip install -r requirements.txt
echo Backend installed. Starting...
start "Backend 8000" cmd /k "uvicorn app:app --reload --port 8000"

timeout /t 8 >nul

echo Installing Frontend...
cd /d "!ET_V2_DIR!frontend"
call npm install
echo Frontend ready. Starting...
start "Frontend 3001" cmd /k "npm run dev"

echo.
echo ==================== 🚀 ET V2 LIVE ====================
echo Backend:  http://localhost:8000/docs  (Swagger API)
echo Frontend: http://localhost:3001       (React UI)
echo Project path: !ET_V2_DIR!
echo ========================================================
pause


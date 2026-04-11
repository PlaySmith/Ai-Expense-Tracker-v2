@echo off
cd /d "D:\Ai Expense Tracker\ET V2"

echo Installing Backend...
cd backend
call pip install -r requirements.txt
echo Backend installed. Starting...
start "Backend 8000" cmd /k "uvicorn app:app --reload --port 8000"

timeout /t 8 >nul

echo Installing Frontend...
cd ..\frontend
call npm install
echo Frontend ready. Starting...
start "Frontend 3001" cmd /k "npm run dev"

echo.
echo ================= ET V2 LIVE =================
echo Backend: http://localhost:8000/docs
echo Frontend: http://localhost:3001
echo ==============================================
pause


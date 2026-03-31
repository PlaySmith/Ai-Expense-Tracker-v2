@echo off
echo Starting ET V2 - Backend ^& Frontend...

REM Backend terminal
start "ET V2 Backend" cmd /k "cd /d D:\Files\Save\Git\Ai-Expense-Tracker-v2-side\ET V2\backend && echo Installing deps... && pip install -r requirements.txt -q && echo Backend ready! && python -m uvicorn app:app --reload --port 8000"

REM Wait for backend
timeout /t 5 /nobreak >nul

REM Frontend terminal
start "ET V2 Frontend" cmd /k "cd /d D:\Files\Save\Git\Ai-Expense-Tracker-v2-side\ET V2\frontend && echo Installing deps... && npm install && echo Frontend ready! && npm run dev"

echo.
echo 🚀 ET V2 running!
echo Backend: http://localhost:8000/docs
echo Frontend: http://localhost:3001
echo.
pause
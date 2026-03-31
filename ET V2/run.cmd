@echo off
echo Starting ET V2 - Backend ^& Frontend (CMD)...

REM Backend in current window
cd /d ET V2\backend
uvicorn app.main:app --reload --port 8000 --host 0.0.0.0

REM Frontend in new window  
start "Frontend 3001" cmd /k "cd /d ET V2\frontend ^& npm run dev"

echo Backend ^& Frontend launched!
echo Backend: http://localhost:8000/docs
echo Frontend: http://localhost:3001
pause

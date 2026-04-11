#!/bin/bash
echo "Starting ET V2 - Backend & Frontend..."

# Backend (bg)
cd backend
echo "Installing backend deps..."
pip install -r requirements.txt -q &
BACKEND_PID=$!

# Frontend (bg)
(cd ../frontend && echo "Installing frontend deps..." && npm install && npm run dev) &

echo "🚀 ET V2 running!"
echo "Backend: http://localhost:8000/docs"
echo "Frontend: http://localhost:3001"
echo "Stop: Ctrl+C or kill processes"

wait

